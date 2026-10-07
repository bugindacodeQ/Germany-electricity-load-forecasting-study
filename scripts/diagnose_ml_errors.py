"""Segment existing ML benchmark errors for validation and historical-reference periods."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "ml_predictions.csv"
OUTPUT = ROOT / "data" / "processed"
REPORT = ROOT / "reports" / "ml_error_diagnostics.md"


def summarize(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    data = frame.copy()
    data["gb_abs_error"] = (data.gradient_boosting_mw - data.actual_mw).abs()
    data["published_abs_error"] = (data.published_day_ahead - data.actual_mw).abs()
    data["gb_minus_published_mae"] = data.published_abs_error - data.gb_abs_error
    data["gb_bias"] = data.gradient_boosting_mw - data.actual_mw
    data["published_bias"] = data.published_day_ahead - data.actual_mw
    return data.groupby(groups, observed=True).agg(
        hours=("actual_mw", "size"),
        gradient_boosting_mae_mw=("gb_abs_error", "mean"),
        published_mae_mw=("published_abs_error", "mean"),
        mae_gain_mw=("gb_minus_published_mae", "mean"),
        gradient_boosting_bias_mw=("gb_bias", "mean"),
        published_bias_mw=("published_bias", "mean"),
    ).reset_index().round(1)


def table_markdown(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    data = pd.read_csv(SOURCE, parse_dates=["utc_timestamp"])
    local = data.utc_timestamp.dt.tz_convert("Europe/Berlin")
    data["local_month"] = local.dt.strftime("%Y-%m")
    data["local_hour"] = local.dt.hour
    data["local_weekday"] = local.dt.day_name()
    data["demand_decile"] = pd.qcut(data.actual_mw, 10, labels=False, duplicates="drop") + 1

    by_month = summarize(data, ["period", "local_month"])
    test = data.loc[data.period == "historical_reference_2020"]
    by_hour = summarize(test, ["local_hour"])
    by_weekday = summarize(test, ["local_weekday"])
    by_demand = summarize(test, ["demand_decile"])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    by_month.to_csv(OUTPUT / "diagnostics_month.csv", index=False)
    by_hour.to_csv(OUTPUT / "diagnostics_hour.csv", index=False)
    by_weekday.to_csv(OUTPUT / "diagnostics_weekday.csv", index=False)
    by_demand.to_csv(OUTPUT / "diagnostics_demand_decile.csv", index=False)

    # Paired daily block bootstrap of the 2020 mean hourly absolute-error gain.
    # Positive means gradient boosting has lower MAE than the published forecast.
    test = test.copy()
    test["gain"] = (test.published_day_ahead - test.actual_mw).abs() - (test.gradient_boosting_mw - test.actual_mw).abs()
    daily = test.groupby(test.utc_timestamp.dt.floor("D").dt.date).gain.mean().to_numpy()
    rng = np.random.default_rng(42)
    draws = rng.choice(daily, size=(10_000, len(daily)), replace=True).mean(axis=1)
    ci_low, ci_high = np.quantile(draws, [0.025, 0.975])

    weakest = by_month.loc[by_month.period == "historical_reference_2020"].nsmallest(3, "mae_gain_mw")
    report = f"""# Error diagnostics by time and demand level

Positive MAE gain means gradient boosting has lower absolute error than the published forecast. These slices are diagnostic, not new model-selection evidence. Grouping uses German local time. The 2020 historical-reference cutoff was defined in UTC, so its final local month contains only the last two hours of October.

Across {len(daily)} previously inspected reference days, mean daily hourly-MAE gain was {daily.mean():.1f} MW. A paired day-level bootstrap (10,000 resamples, seed 42) gives a 95% interval of {ci_low:.1f} to {ci_high:.1f} MW; it includes zero. Gradient boosting had lower daily MAE on {(daily > 0).sum()} of {len(daily)} days.

## Monthly results

{table_markdown(by_month)}

Weakest 2020 months (negative gain favors the published forecast): {', '.join(f"{r.local_month} ({r.mae_gain_mw:.0f} MW)" for r in weakest.itertuples())}.

## Test-period hour of day

{table_markdown(by_hour)}

## Test-period weekday

{table_markdown(by_weekday)}

## Test-period demand decile

Deciles are calculated within the scored historical-reference period. They are for error diagnosis, not forecast-time features.

{table_markdown(by_demand)}

## Readout

The headline MAE difference is small and varies by month, hour, and load range. Neither forecast dominates in every slice. Do not tune to these 2020 slices. Further changes based on the already-inspected 2017-2019 folds are also exploratory; reserve a later unseen holdout for independent confirmation. The published forecast issue time remains unverified.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT}")
    print(f"2020 daily MAE gain 95% interval: [{ci_low:.1f}, {ci_high:.1f}] MW")
    print("Weakest test months:")
    print(weakest.to_string(index=False))


if __name__ == "__main__":
    main()
