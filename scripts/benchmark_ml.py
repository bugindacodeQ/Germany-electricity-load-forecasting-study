"""Fair hourly load benchmark: linear, tree, and small neural-network models."""

from pathlib import Path

import holidays
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "time_series_60min_singleindex.csv"
PROPHET_2019 = ROOT / "data" / "processed" / "holiday_experiment_2019.csv"
POLICY_2020 = ROOT / "data" / "processed" / "holiday_policy_historical_reference_2020.csv"
OUTPUT = ROOT / "data" / "processed"
REPORT = ROOT / "reports" / "ml_benchmark.md"
SEED = 42
FEATURES = [
    "lag_48h", "lag_168h", "lag_336h",
    "hour_sin", "hour_cos", "weekday_sin", "weekday_cos",
    "annual_sin", "annual_cos", "is_weekend",
    "target_holiday", "lag_168h_holiday",
]


def load_features() -> pd.DataFrame:
    data = pd.read_csv(
        SOURCE,
        usecols=["utc_timestamp", "DE_load_actual_entsoe_transparency", "DE_load_forecast_entsoe_transparency"],
        parse_dates=["utc_timestamp"],
    ).rename(columns={
        "DE_load_actual_entsoe_transparency": "actual_mw",
        "DE_load_forecast_entsoe_transparency": "published_day_ahead",
    }).set_index("utc_timestamp").sort_index()
    if data.index.has_duplicates:
        raise ValueError("Duplicate UTC timestamps")
    data = data.reindex(pd.date_range(data.index.min(), data.index.max(), freq="h", tz="UTC"))
    data.index.name = "utc_timestamp"
    for hours in (48, 168, 336):
        data[f"lag_{hours}h"] = data["actual_mw"].shift(hours)
    local = data.index.tz_convert("Europe/Berlin")
    hour = local.hour.to_numpy()
    weekday = local.dayofweek.to_numpy()
    day_of_year = local.dayofyear.to_numpy()
    data["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    data["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    data["weekday_sin"] = np.sin(2 * np.pi * weekday / 7)
    data["weekday_cos"] = np.cos(2 * np.pi * weekday / 7)
    data["annual_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    data["annual_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)
    data["is_weekend"] = (weekday >= 5).astype(int)
    calendar = holidays.Germany(years=range(2014, 2021))
    data["target_holiday"] = np.fromiter((int(day in calendar) for day in local.date), dtype="int8")
    lag_local = (data.index - pd.Timedelta(days=7)).tz_convert("Europe/Berlin")
    data["lag_168h_holiday"] = np.fromiter((int(day in calendar) for day in lag_local.date), dtype="int8")
    return data.dropna(subset=["actual_mw", "published_day_ahead", *FEATURES])


class SmallNet(nn.Module):
    def __init__(self, input_dim: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x).squeeze(-1)


def neural_predict(train: pd.DataFrame, target: pd.DataFrame) -> np.ndarray:
    torch.manual_seed(SEED)
    torch.set_num_threads(4)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[FEATURES]).astype("float32")
    x_target = scaler.transform(target[FEATURES]).astype("float32")
    y_mean = float(train.actual_mw.mean())
    y_scale = float(train.actual_mw.std())
    y_train = ((train.actual_mw.to_numpy() - y_mean) / y_scale).astype("float32")
    dataset = TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train))
    loader = DataLoader(dataset, batch_size=512, shuffle=True)
    model = SmallNet(len(FEATURES))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()
    model.train()
    for _ in range(35):
        for features, labels in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(features), labels)
            loss.backward()
            optimizer.step()
    model.eval()
    with torch.no_grad():
        prediction = model(torch.from_numpy(x_target)).numpy()
    return prediction * y_scale + y_mean


def predict_models(train: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    x_train, y_train = train[FEATURES], train["actual_mw"]
    x_target = target[FEATURES]
    ridge = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    ridge.fit(x_train, y_train)
    tree = HistGradientBoostingRegressor(
        max_iter=250, learning_rate=0.05, max_leaf_nodes=31,
        max_depth=6, l2_regularization=1.0, random_state=SEED,
    )
    tree.fit(x_train, y_train)
    return pd.DataFrame({
        "utc_timestamp": target.index,
        "ridge_mw": ridge.predict(x_target),
        "gradient_boosting_mw": tree.predict(x_target),
        "neural_net_mw": neural_predict(train, target),
    })


def read_existing(path: Path, year: int) -> pd.DataFrame:
    existing = pd.read_csv(path, parse_dates=["utc_timestamp"])
    existing = existing.loc[existing.utc_timestamp.dt.year == year].copy()
    flagged = (existing.target_holiday == 1) | (existing.lag_holiday == 1)
    if "selected_policy_mw" not in existing:
        existing["selected_policy_mw"] = np.where(
            flagged, existing.holiday_prophet_mw, existing.same_hour_1_week_ago
        )
    return existing[["utc_timestamp", "selected_policy_mw"]]


def main() -> None:
    data = load_features()
    train_2019 = data.loc[data.index < "2019-01-01"]
    validation = data.loc["2019-01-01":"2019-12-31"]
    train_2020 = data.loc[data.index < "2020-01-01"]
    test = data.loc["2020-01-01":"2020-09-30"]
    if min(map(len, (train_2019, validation, train_2020, test))) == 0:
        raise ValueError("A training or evaluation split is empty")
    peak_threshold = float(validation.actual_mw.quantile(0.90))

    outputs = []
    for period, train, target, existing_path, year in (
        ("validation_2019", train_2019, validation, PROPHET_2019, 2019),
        ("historical_reference_2020", train_2020, test, POLICY_2020, 2020),
    ):
        print(f"Fitting {period}: {len(train):,} training hours", flush=True)
        predicted = predict_models(train, target)
        comparison = target[["actual_mw", "published_day_ahead", "lag_168h"]].reset_index()
        comparison = comparison.merge(predicted, on="utc_timestamp", validate="one_to_one")
        comparison = comparison.merge(read_existing(existing_path, year), on="utc_timestamp", validate="one_to_one")
        comparison["period"] = period
        outputs.append(comparison)
    result = pd.concat(outputs, ignore_index=True)
    models = ["lag_168h", "selected_policy_mw", "published_day_ahead", "ridge_mw", "gradient_boosting_mw", "neural_net_mw"]
    rows = []
    for period, group in result.groupby("period", sort=False):
        peak = group.actual_mw >= peak_threshold
        for name in models:
            error = group[name] - group.actual_mw
            rows.append({
                "period": period, "model": name, "hours": len(group),
                "mae_mw": error.abs().mean(),
                "rmse_mw": np.sqrt(error.pow(2).mean()),
                "bias_mw": error.mean(),
                "peak_mae_mw": error[peak].abs().mean(),
            })
    summary = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT / "ml_predictions.csv", index=False)
    summary.to_csv(OUTPUT / "ml_metrics.csv", index=False)
    report = """# Standard ML and neural-network benchmark

All models use the same hourly target and comparison rows. Candidate inputs are known before the assumed 12:00 UTC previous-day cutoff: load 48, 168 and 336 hours before each target, local calendar cycles, and nationwide German holiday flags for target day and the prior-week reference day. Actual same-day generation and prices are excluded.

Ridge and histogram gradient boosting use fixed, untuned settings. The small two-hidden-layer PyTorch network uses 35 fixed training epochs and a fixed seed. Models fit through 2018 for 2019 validation, then refit through 2019 for January-September 2020. That 2020 period was originally designated as a test but has since been inspected; treat it as historical reference only. The holiday-aware policy was selected earlier using 2019. All methods below use the same nonmissing hours.

| Period | Method | Hours | MAE MW | RMSE MW | Bias MW | Peak MAE MW |
|---|---|---:|---:|---:|---:|---:|
"""
    for row in rows:
        report += (
            f"| {row['period']} | {row['model']} | {row['hours']:,} | "
            f"{row['mae_mw']:,.1f} | {row['rmse_mw']:,.1f} | "
            f"{row['bias_mw']:,.1f} | {row['peak_mae_mw']:,.1f} |\n"
        )
    report += "\nThe published forecast issue time is unverified. This is an accuracy comparison, not a savings claim.\n"
    REPORT.write_text(report, encoding="utf-8")
    print(summary.round(1).to_string(index=False))
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
