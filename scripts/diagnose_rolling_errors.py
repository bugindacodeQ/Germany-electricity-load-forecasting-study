"""Describe load and forecast-error patterns across historical validation folds."""
from pathlib import Path

import numpy as np
import pandas as pd
import holidays


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else Path(r"C:\Users\Hp\Desktop\GERMANY_POWER")
OUT = PROJECT / "data" / "processed" if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR / "error_diagnostics"
REPORT = PROJECT / "reports" / "forecast_error_diagnostics.md" if SCRIPT_DIR.name == "scripts" else OUT / "forecast_error_diagnostics.md"
FOLDS = PROJECT / "data" / "processed" / "rolling_validation_predictions.csv"
REFERENCE = PROJECT / "data" / "processed" / "ml_predictions.csv"
RAW = PROJECT / "data" / "raw" / "time_series_60min_singleindex.csv"


def enrich(frame: pd.DataFrame, year_col: str, year_label: str) -> pd.DataFrame:
    x = frame.copy()
    x["utc_timestamp"] = pd.to_datetime(x.utc_timestamp, utc=True)
    local = x.utc_timestamp.dt.tz_convert("Europe/Berlin")
    x["year"] = x[year_col].astype(int) if year_col in x else int(year_label)
    x["month"] = local.dt.month
    x["local_month"] = local.dt.strftime("%Y-%m")
    x["local_hour"] = local.dt.hour
    x["weekday"] = local.dt.day_name()
    holiday_calendar = holidays.Germany(years=range(2014, 2021))
    x["holiday"] = ["holiday" if day in holiday_calendar else "non_holiday" for day in local.dt.date]
    x["season"] = local.dt.month.map({12: "Winter", 1: "Winter", 2: "Winter",
                                      3: "Spring", 4: "Spring", 5: "Spring",
                                      6: "Summer", 7: "Summer", 8: "Summer",
                                      9: "Autumn", 10: "Autumn", 11: "Autumn"})
    x["gb_error"] = x.gradient_boosting_mw - x.actual_mw
    x["published_error"] = x.published_day_ahead - x.actual_mw
    x["naive_error"] = x.same_hour_1_week_ago - x.actual_mw
    return x


def metric_rows(frame: pd.DataFrame, keys: list[str], dimension: str) -> list[pd.DataFrame]:
    rows = []
    for model, error_col in (("gradient_boosting", "gb_error"),
                             ("published_reference", "published_error"),
                             ("weekly_naive", "naive_error")):
        g = frame.groupby(keys, observed=True)[error_col]
        tbl = g.agg(hours="size", bias_mw="mean", mae_mw=lambda s: s.abs().mean(),
                    rmse_mw=lambda s: np.sqrt(np.mean(np.square(s)))).reset_index()
        tbl["model"] = model
        tbl["slice"] = dimension
        rows.append(tbl)
    return rows


def md_table(frame: pd.DataFrame, columns: list[str]) -> str:
    x = frame[columns].copy()
    for col in x.select_dtypes(include="number").columns:
        if col == "hours":
            x[col] = x[col].map(lambda v: f"{v:,.0f}" if pd.notna(v) else "")
        elif col in {"year", "local_hour", "demand_decile"}:
            x[col] = x[col].map(lambda v: f"{v:.0f}" if pd.notna(v) else "")
        else:
            x[col] = x[col].map(lambda v: f"{v:,.1f}" if pd.notna(v) else "")
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    lines.extend("| " + " | ".join(map(str, row)) + " |" for row in x.itertuples(index=False, name=None))
    return "\n".join(lines)


def main() -> None:
    folds = pd.read_csv(FOLDS, parse_dates=["utc_timestamp"])
    folds = folds.rename(columns={"validation_year": "year"})
    folds["same_hour_1_week_ago"] = folds.same_hour_1_week_ago
    fold_data = enrich(folds, "year", "")

    ref = pd.read_csv(REFERENCE, parse_dates=["utc_timestamp"])
    ref = ref.loc[ref.period.eq("historical_reference_2020")].copy()
    ref["same_hour_1_week_ago"] = ref.lag_168h
    ref["year"] = 2020
    reference = enrich(ref, "year", "")
    data = pd.concat([fold_data, reference], ignore_index=True)

    data["validation_period"] = np.where(data.year.eq(2020), "2020_reference", "validation")
    data["demand_decile"] = data.groupby("year").actual_mw.transform(
        lambda s: pd.qcut(s, 10, labels=False, duplicates="drop") + 1)
    slices = []
    for period in ("validation", "2020_reference"):
        part = data.loc[data.validation_period.eq(period)]
        for dimension, keys in (("year", ["year"]), ("season", ["year", "season"]),
                                ("local_hour", ["year", "local_hour"]),
                                ("weekday", ["year", "weekday"]),
                                ("holiday", ["year", "holiday"]),
                                ("demand_decile", ["year", "demand_decile"])):
            slices.extend(metric_rows(part, keys, dimension))
    error_slices = pd.concat(slices, ignore_index=True).round(2)

    raw = pd.read_csv(RAW, usecols=["utc_timestamp", "DE_load_actual_entsoe_transparency"],
                      parse_dates=["utc_timestamp"])
    raw = raw.rename(columns={"DE_load_actual_entsoe_transparency": "actual_mw"})
    raw["utc_timestamp"] = pd.to_datetime(raw.utc_timestamp, utc=True)
    raw = raw.dropna(subset=["actual_mw"])
    local = raw.utc_timestamp.dt.tz_convert("Europe/Berlin")
    raw["year"] = local.dt.year
    raw["local_month"] = local.dt.strftime("%Y-%m")
    annual = raw.groupby("year").actual_mw.agg(
        hours="count", mean_mw="mean", median_mw="median", std_mw="std",
        p05_mw=lambda s: s.quantile(.05), p95_mw=lambda s: s.quantile(.95)).reset_index()
    monthly = raw.groupby(["year", "local_month"]).actual_mw.agg(
        hours="count", mean_mw="mean", median_mw="median", std_mw="std").reset_index()
    monthly["change_from_previous_month_mw"] = monthly.mean_mw.diff()

    OUT.mkdir(parents=True, exist_ok=True)
    error_slices.to_csv(OUT / "fold_error_slices.csv", index=False)
    annual.to_csv(OUT / "annual_load_distribution.csv", index=False)
    monthly.to_csv(OUT / "monthly_load_distribution.csv", index=False)

    headline = error_slices.loc[error_slices.slice.eq("year")]
    yearly = headline.pivot(index="year", columns="model", values=["mae_mw", "bias_mw"]).round(1)
    season = error_slices.loc[error_slices.slice.eq("season") & error_slices.model.eq("gradient_boosting")]
    hour = error_slices.loc[error_slices.slice.eq("local_hour") & error_slices.model.eq("gradient_boosting")]
    weekday = error_slices.loc[error_slices.slice.eq("weekday") & error_slices.model.eq("gradient_boosting")]
    holiday = error_slices.loc[error_slices.slice.eq("holiday") & error_slices.model.eq("gradient_boosting")]
    complete_months = monthly.loc[monthly.hours.ge(600)]
    extremes = pd.concat([complete_months.nsmallest(5, "mean_mw"),
                          complete_months.nlargest(5, "mean_mw")]).drop_duplicates()
    report = f"""# Error patterns and historical load shifts

This is descriptive diagnosis. The 2017–2019 validation folds were already inspected and remain development evidence; 2020 is a previously viewed reference period. Do not use these slices to tune and then present the same periods as independent confirmation. Grouping uses Europe/Berlin local time. Load deciles are calculated within each scored year and are diagnostic only.

## Annual forecast error

{md_table(headline.sort_values(["year", "model"]), ["year", "model", "hours", "mae_mw", "rmse_mw", "bias_mw"])}

Positive bias means forecast minus actual (overforecast); negative bias means underforecast.

## Gradient boosting by local season

{md_table(season.sort_values(["year", "season"]), ["year", "season", "hours", "mae_mw", "bias_mw"])}

## Gradient boosting by local hour

{md_table(hour.sort_values(["year", "local_hour"]), ["year", "local_hour", "hours", "mae_mw", "bias_mw"])}

## Gradient boosting by weekday

{md_table(weekday.sort_values(["year", "weekday"]), ["year", "weekday", "hours", "mae_mw", "bias_mw"])}

## Gradient boosting on holidays

Holiday flags use the Germany public-holiday calendar and local dates. National holidays are a coarse proxy; regional holidays and special bridge days are not encoded.

{md_table(holiday.sort_values(["year", "holiday"]), ["year", "holiday", "hours", "mae_mw", "bias_mw"])}

## Annual load distribution

{md_table(annual, ["year", "hours", "mean_mw", "median_mw", "std_mw", "p05_mw", "p95_mw"])}

## Lowest and highest monthly average load

{md_table(extremes.sort_values("local_month"), ["local_month", "hours", "mean_mw", "median_mw", "std_mw", "change_from_previous_month_mw"])}

## What the evidence says

- The published forecast's bias changes substantially between folds; gradient boosting's bias is smaller and changes sign between folds. This is a measured pattern, not an explanation for why it occurred.
- Gradient boosting error varies by season and local hour. In these folds, daytime/late-afternoon hours are often harder than overnight hours; inspect the hour table for year-specific differences rather than treating that as universal.
- Public-holiday hours have higher gradient-boosting MAE than non-holiday hours in every scored year, based on only 143–240 holiday hours per period. Holiday bias also changes direction between years, so the pattern warrants checking holiday definitions and special days before any feature change.
- Monthly average load has visible variation, including the 2020 spring reference period. This flags a possible regime or composition change for follow-up; it does not establish a structural break or its cause.
- The current predictions contain no archived weather forecasts, source-vintage history, or operating covariates. Weather, pandemic-related behavior, holidays, reporting changes, and methodology changes remain hypotheses until matched to evidence.
- Residual autocorrelation and formal change-point testing are not established in this pass. They need explicit analysis before making those claims. The final 2020 local October fragment (two hours) is excluded from monthly extrema summaries.

## Artifacts

- `data/processed/fold_error_slices.csv`
- `data/processed/annual_load_distribution.csv`
- `data/processed/monthly_load_distribution.csv`
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT}")
    print(headline.sort_values(["year", "model"]).round(1).to_string(index=False))
    print("Top/bottom gradient boosting MAE slices:")
    print(season.sort_values("mae_mw").groupby("year").head(1).round(1).to_string(index=False))
    print(season.sort_values("mae_mw").groupby("year").tail(1).round(1).to_string(index=False))


if __name__ == "__main__":
    main()
