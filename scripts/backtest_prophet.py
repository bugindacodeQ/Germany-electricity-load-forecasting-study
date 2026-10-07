"""Monthly-refit Prophet backtest for next-day German hourly load."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from prophet import Prophet


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "time_series_60min_singleindex.csv"
BASELINES = ROOT / "data" / "processed" / "baseline_predictions.csv"
OUT = ROOT / "data" / "processed"
REPORT = ROOT / "reports" / "prophet_backtest.md"
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


def metrics(data: pd.DataFrame, prediction: str, peak_threshold: float) -> dict:
    error = data[prediction] - data["actual_mw"]
    peak = data["actual_mw"] >= peak_threshold
    return {
        "n_hours": int(len(data)),
        "mae_mw": float(error.abs().mean()),
        "rmse_mw": float(np.sqrt(error.pow(2).mean())),
        "bias_mw": float(error.mean()),
        "peak_mae_mw": float(error[peak].abs().mean()),
        "peak_hours": int(peak.sum()),
    }


def main() -> None:
    if not SOURCE.exists() or not BASELINES.exists():
        raise SystemExit("Run scripts/backtest_baselines.py first and check the source CSV.")

    data = pd.read_csv(
        SOURCE,
        usecols=["utc_timestamp", "DE_load_actual_entsoe_transparency"],
        parse_dates=["utc_timestamp"],
    ).rename(columns={"DE_load_actual_entsoe_transparency": "actual_mw"})
    data = data.set_index("utc_timestamp").sort_index()
    if data.index.has_duplicates:
        raise ValueError("Duplicate UTC timestamps")
    data = data.reindex(pd.date_range(data.index.min(), data.index.max(), freq="h", tz="UTC"))
    data.index.name = "utc_timestamp"
    data["lag_168h"] = data["actual_mw"].shift(168)

    results = []
    for month_start in pd.date_range("2019-01-01", "2020-09-01", freq="MS", tz="UTC"):
        month_end = month_start + pd.offsets.MonthBegin(1)
        train_start = month_start - pd.DateOffset(years=2)
        train = data.loc[(data.index >= train_start) & (data.index < month_start)].dropna()
        target = data.loc[(data.index >= month_start) & (data.index < month_end)].dropna(subset=["lag_168h"])
        if len(train) < 15_000:
            raise ValueError(f"Insufficient training rows for {month_start:%Y-%m}: {len(train)}")
        if target.empty:
            continue

        # All lag values are one week old. Thus, each is known before the
        # previous day's assumed 12:00 UTC issue cutoff.
        train_frame = pd.DataFrame({
            "ds": train.index.tz_localize(None),
            "y": train["actual_mw"].to_numpy(),
            "lag_168h": train["lag_168h"].to_numpy(),
        })
        target_frame = pd.DataFrame({
            "ds": target.index.tz_localize(None),
            "lag_168h": target["lag_168h"].to_numpy(),
        })
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            uncertainty_samples=0,
        )
        model.add_regressor("lag_168h", standardize=True)
        model.fit(train_frame)
        prediction = model.predict(target_frame)
        results.append(pd.DataFrame({
            "utc_timestamp": target.index,
            "prophet_mw": prediction["yhat"].to_numpy(),
            "fit_month": month_start.strftime("%Y-%m"),
            "training_rows": len(train),
        }))
        print(f"Finished {month_start:%Y-%m}: {len(target):,} predicted hours", flush=True)

    predicted = pd.concat(results, ignore_index=True)
    baseline = pd.read_csv(BASELINES, parse_dates=["utc_timestamp"])
    compared = baseline.merge(predicted, on="utc_timestamp", how="inner", validate="one_to_one")
    compared = compared.dropna(subset=["actual_mw", "same_hour_1_week_ago", "published_day_ahead", "prophet_mw"])
    validation = compared.loc[compared.utc_timestamp.dt.year == 2019]
    test = compared.loc[compared.utc_timestamp.dt.year == 2020]
    peak_threshold = float(validation["actual_mw"].quantile(0.90))
    rows = []
    for period, subset in (("validation_2019", validation), ("historical_reference_2020", test)):
        for model in ("same_hour_1_week_ago", "published_day_ahead", "prophet_mw"):
            rows.append({"period": period, "model": model, **metrics(subset, model, peak_threshold)})
    summary = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    predicted.to_csv(OUT / "prophet_predictions.csv", index=False)
    compared.to_csv(OUT / "prophet_comparison.csv", index=False)
    summary.to_csv(OUT / "prophet_metrics.csv", index=False)

    report = """# Prophet day-ahead backtest

Prophet is refitted at the beginning of each month on the previous two years of hourly data. It predicts every hour of that month using calendar seasonality and load from the same hour one week earlier. That lag is known before an assumed 12:00 UTC cutoff on the previous day. The model parameters remain fixed within each month; the lag input updates as historical observations become available. No test-month actual load enters model fitting until a later month's refit.

The original split used 2019 for validation and January-September 2020 as a final test. Both periods have since been inspected; 2020 is a historical reference, not an untouched test. All methods below use identical hours. Peak demand is defined using the validation period 90th percentile. The published forecast issue time remains unverified.

| Period | Method | Hours | MAE MW | RMSE MW | Bias MW | Peak MAE MW |
|---|---|---:|---:|---:|---:|---:|
"""
    for row in rows:
        report += (
            f"| {row['period']} | {row['model']} | {row['n_hours']:,} | "
            f"{row['mae_mw']:,.1f} | {row['rmse_mw']:,.1f} | "
            f"{row['bias_mw']:,.1f} | {row['peak_mae_mw']:,.1f} |\n"
        )
    report += """
## Limits

The monthly refit schedule is a computational and operational choice; it is not a daily refit. The 2020 reference period includes demand shifts during the COVID-19 pandemic. These aggregate grid results do not measure a specific company's savings. A separate cost model and operational data would be needed for that claim.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(summary.round(1).to_string(index=False))
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
