"""Evaluate leakage-safe day-ahead load baselines against the published forecast."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "time_series_60min_singleindex.csv"
OUTPUT = ROOT / "data" / "processed"
REPORT = ROOT / "reports" / "baseline_backtest.md"
ACTUAL = "DE_load_actual_entsoe_transparency"
PUBLISHED = "DE_load_forecast_entsoe_transparency"
BASELINES = ("same_hour_2_days_ago", "same_hour_1_week_ago", "lag_blend")
MODELS = (*BASELINES, "published_day_ahead")


def scores(data: pd.DataFrame, prediction: str, peak_threshold: float) -> dict:
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
    if not SOURCE.is_file():
        raise SystemExit(f"Missing CSV: {SOURCE}")
    data = pd.read_csv(
        SOURCE,
        usecols=["utc_timestamp", ACTUAL, PUBLISHED],
        parse_dates=["utc_timestamp"],
    ).rename(columns={ACTUAL: "actual_mw", PUBLISHED: "published_day_ahead"})
    data = data.set_index("utc_timestamp").sort_index()
    if data.index.has_duplicates:
        raise ValueError("Duplicate UTC timestamps")
    if not data.index.is_monotonic_increasing:
        raise ValueError("Unsorted UTC timestamps")

    # Reindex to a complete hourly UTC grid so shifts always mean elapsed hours.
    grid = pd.date_range(data.index.min(), data.index.max(), freq="h", tz="UTC")
    data = data.reindex(grid)
    data.index.name = "utc_timestamp"
    data["same_hour_2_days_ago"] = data["actual_mw"].shift(48)
    data["same_hour_1_week_ago"] = data["actual_mw"].shift(168)
    data["lag_blend"] = (data["same_hour_2_days_ago"] + data["same_hour_1_week_ago"]) / 2

    # At an assumed 12:00 UTC cutoff on the previous day, 48h and 168h lags
    # precede the cutoff for every target hour. This assumption is explicit.
    common = data.dropna(subset=["actual_mw", *MODELS]).copy()
    common = common.loc["2019-01-01":"2020-09-30"]
    validation = common.loc["2019-01-01":"2019-12-31"]
    test = common.loc["2020-01-01":"2020-09-30"]
    if validation.empty or test.empty:
        raise ValueError("Validation or test period is empty")
    peak_threshold = float(validation["actual_mw"].quantile(0.90))

    rows = []
    for period, subset in (("validation_2019", validation), ("historical_reference_2020", test)):
        for model in MODELS:
            rows.append({"period": period, "model": model, **scores(subset, model, peak_threshold)})
    metrics = pd.DataFrame(rows)
    selected = metrics.loc[
        (metrics.period == "validation_2019") & metrics.model.isin(BASELINES)
    ].sort_values("mae_mw").iloc[0]["model"]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    common.reset_index().to_csv(OUTPUT / "baseline_predictions.csv", index=False)
    metrics.to_csv(OUTPUT / "baseline_metrics.csv", index=False)
    val_count = len(validation)
    test_count = len(test)
    report = f"""# Day-ahead baseline backtest

## Decision and forecast definition

Forecast Germany's hourly load (MW) for the next UTC calendar day. We assume forecasts are issued at 12:00 UTC on the previous day. This is a study assumption, not a verified ENTSO-E submission time. The 48-hour and 168-hour lags are available before that cutoff for every target hour. The published day-ahead forecast is an external comparator; its precise issue time still needs verification.

## Evaluation

- Validation: 2019 ({val_count:,} common hours). Choose the strongest simple baseline by MAE only here.
- Historical reference: January-September 2020 ({test_count:,} common hours). This period was originally designated as the test but has since been inspected; it is not an untouched final test.
- Candidate baselines: same hour two days ago, same hour one week ago, and their equal-weight blend.
- Selected baseline on validation: **{selected}**.
- Peak threshold: {peak_threshold:,.1f} MW, the 90th percentile of validation load. Peak MAE uses this fixed threshold in both periods.
- Forecast error = prediction minus actual. Positive bias means overforecasting.

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
## Interpretation limits

This is a historical national-load backtest, not a measured saving for a company. 2020 includes unusual demand conditions, so the test is also a shift check. National load is not transferable directly to a plant or mini-grid. Before assessing financial value, obtain the actual operating decision, cost of over/underforecasting, and published forecast issue-time metadata. Before trying Prophet or another model, preserve these test dates and the common-hour comparison.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(metrics.round(1).to_string(index=False))
    print(f"Selected baseline: {selected}")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
