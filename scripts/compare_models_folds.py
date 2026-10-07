"""Compare locked model specifications on identical annual expanding folds."""
from pathlib import Path
import logging
import sys

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_FOR_IMPORT = _SCRIPT_DIR.parent if _SCRIPT_DIR.name == "scripts" else Path(r"C:\Users\Hp\Desktop\GERMANY_POWER")
sys.path.insert(0, str(_PROJECT_FOR_IMPORT / "scripts"))
from benchmark_ml import FEATURES, SEED, load_features, neural_predict


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else Path(r"C:\Users\Hp\Desktop\GERMANY_POWER")
OUT = PROJECT / "data" / "processed" if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR / "model_comparison"
REPORT = PROJECT / "reports" / "expanding_window_model_comparison.md" if SCRIPT_DIR.name == "scripts" else OUT / "expanding_window_model_comparison.md"
YEARS = (2017, 2018, 2019)
MODELS = ["same_hour_48h", "same_hour_168h", "ridge", "gradient_boosting", "neural_network", "prophet", "published_reference"]
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


def fit_predict(train: pd.DataFrame, validation: pd.DataFrame) -> dict[str, np.ndarray]:
    x_train, x_valid = train[FEATURES], validation[FEATURES]
    ridge = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    ridge.fit(x_train, train.actual_mw)
    boosting = HistGradientBoostingRegressor(
        max_iter=250, learning_rate=0.05, max_leaf_nodes=31,
        max_depth=6, l2_regularization=1.0, random_state=SEED,
    )
    boosting.fit(x_train, train.actual_mw)

    prophet_train = pd.DataFrame({
        "ds": train.index.tz_localize(None),
        "y": train.actual_mw.to_numpy(),
        "lag_168h": train.lag_168h.to_numpy(),
    })
    prophet_valid = pd.DataFrame({
        "ds": validation.index.tz_localize(None),
        "lag_168h": validation.lag_168h.to_numpy(),
    })
    prophet = Prophet(daily_seasonality=True, weekly_seasonality=True,
                      yearly_seasonality=True, uncertainty_samples=0)
    prophet.add_regressor("lag_168h", standardize=True)
    prophet.fit(prophet_train)
    prophet_prediction = prophet.predict(prophet_valid)["yhat"].to_numpy()

    return {
        "same_hour_48h": validation.lag_48h.to_numpy(),
        "same_hour_168h": validation.lag_168h.to_numpy(),
        "ridge": ridge.predict(x_valid),
        "gradient_boosting": boosting.predict(x_valid),
        "neural_network": neural_predict(train, validation),
        "prophet": prophet_prediction,
        "published_reference": validation.published_day_ahead.to_numpy(),
    }


def score(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, frame in predictions.groupby("year", sort=True):
        threshold = float(frame.training_p90.iloc[0])
        peak = frame.actual_mw >= threshold
        for model in MODELS:
            error = frame[model] - frame.actual_mw
            rows.append({
                "year": year, "model": model, "hours": len(frame),
                "mae_mw": error.abs().mean(),
                "rmse_mw": np.sqrt(np.mean(np.square(error))),
                "bias_mw": error.mean(),
                "high_load_mae_mw": error[peak].abs().mean(),
                "high_load_threshold_mw": threshold,
                "high_load_hours": int(peak.sum()),
            })
    for model in MODELS:
        frame = predictions
        error = frame[model] - frame.actual_mw
        peak = frame.actual_mw >= frame.training_p90
        rows.append({
            "year": "pooled_oof", "model": model, "hours": len(frame),
            "mae_mw": error.abs().mean(),
            "rmse_mw": np.sqrt(np.mean(np.square(error))),
            "bias_mw": error.mean(),
            "high_load_mae_mw": error[peak].abs().mean(),
            "high_load_threshold_mw": np.nan,
            "high_load_hours": int(peak.sum()),
        })
    return pd.DataFrame(rows)


def paired_day_bootstrap(predictions: pd.DataFrame, candidate: str, reference: str,
                         draws: int = 10_000, seed: int = 42) -> dict:
    x = predictions.copy()
    x["day_utc"] = x.utc_timestamp.dt.floor("D")
    x["gain_mw"] = (x[reference] - x.actual_mw).abs() - (x[candidate] - x.actual_mw).abs()
    # Positive gain means candidate has lower MAE than reference.
    daily = x.groupby(["year", "day_utc"], observed=True).gain_mw.mean().reset_index()
    point = x.gain_mw.mean()
    rng = np.random.default_rng(seed)
    sampled_by_year = []
    for _, group in daily.groupby("year", sort=True):
        values = group.gain_mw.to_numpy()
        sampled_by_year.append(rng.choice(values, size=(draws, len(values)), replace=True))
    pooled = np.concatenate(sampled_by_year, axis=1).mean(axis=1)
    low, high = np.quantile(pooled, [0.025, 0.975])
    return {"candidate": candidate, "reference": reference,
            "mae_gain_mw_candidate_better_positive": point,
            "ci95_low_mw": low, "ci95_high_mw": high,
            "bootstrap_days": len(daily), "draws": draws}


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    out = frame[columns].copy()
    for column in columns:
        if column == "year":
            out[column] = out[column].map(lambda v: str(int(v)) if pd.notna(v) and str(v) != "pooled_oof" else str(v))
        elif column in {"hours", "high_load_hours", "bootstrap_days", "draws"}:
            out[column] = out[column].map(lambda v: f"{int(v):,}" if pd.notna(v) and str(v) != "pooled_oof" else str(v))
        elif pd.api.types.is_numeric_dtype(out[column]):
            out[column] = out[column].map(lambda v: f"{v:,.1f}" if pd.notna(v) else "")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    lines.extend("| " + " | ".join(map(str, row)) + " |" for row in out.itertuples(index=False, name=None))
    return "\n".join(lines)


def main() -> None:
    data = load_features()
    outputs = []
    for year in YEARS:
        train = data.loc[data.index < f"{year}-01-01"]
        validation = data.loc[data.index.year == year]
        if train.empty or validation.empty:
            raise ValueError(f"Empty data in fold {year}")
        predictions = fit_predict(train, validation)
        result = pd.DataFrame({"utc_timestamp": validation.index,
                               "actual_mw": validation.actual_mw.to_numpy(),
                               "year": year,
                               "training_hours": len(train),
                               "training_p90": float(train.actual_mw.quantile(.90)),
                               **predictions})
        outputs.append(result)
        print(f"Scored {year}: train={len(train):,}, validation={len(validation):,}", flush=True)

    all_predictions = pd.concat(outputs, ignore_index=True)
    metrics = score(all_predictions)
    fold_metrics = metrics.loc[metrics.year.ne("pooled_oof")].copy()
    fold_metrics["year"] = fold_metrics.year.astype(int)
    gb_by_year = fold_metrics.loc[fold_metrics.model.eq("gradient_boosting")].set_index("year").mae_mw
    fold_metrics = metrics.loc[metrics.year.ne("pooled_oof")].copy()
    fold_metrics["year"] = fold_metrics.year.astype(int)
    gb_by_year = fold_metrics.loc[fold_metrics.model.eq("gradient_boosting")].set_index("year").mae_mw
    fold_metrics = metrics.loc[metrics.year.ne("pooled_oof")].copy()
    fold_metrics["year"] = fold_metrics.year.astype(int)
    gb_by_year = fold_metrics.loc[fold_metrics.model.eq("gradient_boosting")].set_index("year").mae_mw
    comparisons_list = []
    candidates = ["same_hour_48h", "ridge", "gradient_boosting", "neural_network", "prophet"]
    for ref_index, reference in enumerate(["same_hour_168h", "published_reference"]):
        for model_index, model in enumerate(candidates):
            comparisons_list.append(paired_day_bootstrap(
                all_predictions, model, reference, seed=42 + ref_index * 10 + model_index))
    for model_index, model in enumerate(["neural_network", "ridge", "prophet", "published_reference", "same_hour_168h"]):
        comparisons_list.append(paired_day_bootstrap(
            all_predictions, model, "gradient_boosting", seed=62 + model_index))
    comparisons = pd.DataFrame(comparisons_list)
    nn_vs_gb = comparisons.loc[
        comparisons.candidate.eq("neural_network") & comparisons.reference.eq("gradient_boosting")
    ].iloc[0]
    gb_vs_naive = comparisons.loc[
        comparisons.candidate.eq("gradient_boosting") & comparisons.reference.eq("same_hour_168h")
    ].iloc[0]
    gb_vs_published = comparisons.loc[
        comparisons.candidate.eq("gradient_boosting") & comparisons.reference.eq("published_reference")
    ].iloc[0]
    nn_by_year = fold_metrics.loc[fold_metrics.model.eq("neural_network")].set_index("year").mae_mw
    published_by_year = fold_metrics.loc[fold_metrics.model.eq("published_reference")].set_index("year").mae_mw
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    all_predictions.to_csv(OUT / "expanding_fold_predictions.csv", index=False)
    metrics.to_csv(OUT / "expanding_fold_metrics.csv", index=False)
    comparisons.to_csv(OUT / "paired_model_comparisons.csv", index=False)

    pooled = metrics.loc[metrics.year.eq("pooled_oof")].sort_values("mae_mw")
    report = f"""# Expanding-window model comparison

## Design

All models are evaluated on the same nonmissing timestamps in 2017, 2018, and 2019. Each learned model is fitted once at the start of each year using only prior data, then held fixed for that year. Lag and calendar features update by target timestamp. Specifications are fixed: Ridge alpha=10; histogram gradient boosting (250 iterations, learning rate 0.05, 31 leaves, depth 6, L2=1); the two-hidden-layer PyTorch network (64/32 units, 35 epochs, seed 42); and Prophet with daily/weekly/yearly seasonality plus a 168-hour load regressor. Scaling is fitted on training data only. No hyperparameter search was performed in this benchmark.

The holiday-aware policy is omitted from fold selection because its rule was selected using 2019, so scoring it on 2019 would reuse its selection data. The OPSD published forecast is retained as an external historical reference; its issue/revision vintage is unknown. These folds have already been inspected in earlier work, so all results below remain exploratory development evidence. Prophet emitted a warning that the first fold has fewer than two years of training history for yearly seasonality; interpret that fold's Prophet result cautiously.

## Fold results

{markdown_table(fold_metrics.sort_values(["year", "mae_mw"]), ["year", "model", "hours", "mae_mw", "rmse_mw", "bias_mw", "high_load_mae_mw"])}

## Pooled out-of-fold results

{markdown_table(pooled, ["model", "hours", "mae_mw", "rmse_mw", "bias_mw", "high_load_mae_mw"])}

High load is defined within each fold using that fold's training-set 90th percentile. Bias is prediction minus actual; positive is overforecast.

## Paired day-level uncertainty

{markdown_table(comparisons, ["candidate", "reference", "mae_gain_mw_candidate_better_positive", "ci95_low_mw", "ci95_high_mw", "bootstrap_days"])}

Positive paired gain means the candidate's absolute error is lower. Comparisons include each candidate against the weekly naive and published reference, plus candidate checks against gradient boosting. The 95% intervals resample whole UTC days independently within each fold (10,000 draws), preserving within-day dependence. They do not account for all between-day serial dependence, and should be treated as approximate.

## Decision readout

- Gradient boosting had the lowest pooled hourly MAE at {metrics.loc[(metrics.year == 'pooled_oof') & (metrics.model == 'gradient_boosting'), 'mae_mw'].iloc[0]:,.1f} MW. It beat the weekly-naive baseline by {gb_vs_naive.mae_gain_mw_candidate_better_positive:,.1f} MW; the paired day-bootstrap 95% interval was [{gb_vs_naive.ci95_low_mw:,.1f}, {gb_vs_naive.ci95_high_mw:,.1f}] MW.
- Neural network was the closest learned model (annual MAEs {nn_by_year[2017]:,.1f}, {nn_by_year[2018]:,.1f}, {nn_by_year[2019]:,.1f} MW). Its pooled advantage over gradient boosting was {nn_vs_gb.mae_gain_mw_candidate_better_positive:,.1f} MW, with 95% interval [{nn_vs_gb.ci95_low_mw:,.1f}, {nn_vs_gb.ci95_high_mw:,.1f}] MW; the interval includes zero, so these folds do not establish a clear difference between the two.
- Gradient boosting MAEs were {gb_by_year[2017]:,.1f}, {gb_by_year[2018]:,.1f}, and {gb_by_year[2019]:,.1f} MW. The published reference was slightly better in 2017 and 2018 ({published_by_year[2017]:,.1f} and {published_by_year[2018]:,.1f} MW) but much worse in 2019 ({published_by_year[2019]:,.1f} MW). Its issue/revision vintage is unverified, so the pooled gain of {gb_vs_published.mae_gain_mw_candidate_better_positive:,.1f} MW is only a historical export comparison.
- Ridge and the current Prophet specification underperformed gradient boosting on these folds. Prophet's first fold also triggered a short-history warning for yearly seasonality; this diagnoses this specification, not Prophet as a whole.
- Treat these model rankings as exploratory because all three folds have already been inspected. They guide what to test later; they do not provide independent confirmation.
- The 2020 period was not used here and remains a previously viewed historical reference, not a fresh test.
- Do not claim financial value from MW errors. A later unseen holdout, confirmed target/cutoff, and a stakeholder cost model are still required.

## Artifacts

- `data/processed/expanding_fold_predictions.csv`
- `data/processed/expanding_fold_metrics.csv`
- `data/processed/paired_model_comparisons.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print("Pooled out-of-fold metrics (MW):")
    print(pooled.round(1).to_string(index=False))
    print("Paired comparisons:")
    print(comparisons.round(1).to_string(index=False))
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
