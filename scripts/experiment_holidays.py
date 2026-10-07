"""Test holiday-aware Prophet against the existing 2019 validation forecast."""

import logging
from pathlib import Path

import holidays
import numpy as np
import pandas as pd
from prophet import Prophet


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "time_series_60min_singleindex.csv"
COMPARISON = ROOT / "data" / "processed" / "prophet_comparison.csv"
OUT = ROOT / "data" / "processed" / "holiday_experiment_2019.csv"
REPORT = ROOT / "reports" / "holiday_experiment_2019.md"
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


def main() -> None:
    data = pd.read_csv(
        SOURCE,
        usecols=["utc_timestamp", "DE_load_actual_entsoe_transparency"],
        parse_dates=["utc_timestamp"],
    ).rename(columns={"DE_load_actual_entsoe_transparency": "actual_mw"})
    data = data.set_index("utc_timestamp").sort_index()
    data = data.reindex(pd.date_range(data.index.min(), data.index.max(), freq="h", tz="UTC"))
    data.index.name = "utc_timestamp"
    data["lag_168h"] = data["actual_mw"].shift(168)
    calendar = holidays.Germany(years=range(2015, 2021))
    local_dates = data.index.tz_convert("Europe/Berlin").date
    lag_local_dates = (data.index - pd.Timedelta(days=7)).tz_convert("Europe/Berlin").date
    data["target_holiday"] = np.fromiter((int(day in calendar) for day in local_dates), dtype="int8")
    data["lag_holiday"] = np.fromiter((int(day in calendar) for day in lag_local_dates), dtype="int8")

    frames = []
    for month_start in pd.date_range("2019-01-01", "2019-12-01", freq="MS", tz="UTC"):
        month_end = month_start + pd.offsets.MonthBegin(1)
        train_start = month_start - pd.DateOffset(years=2)
        train = data.loc[(data.index >= train_start) & (data.index < month_start)].dropna(subset=["actual_mw", "lag_168h"])
        target = data.loc[(data.index >= month_start) & (data.index < month_end)].dropna(subset=["lag_168h"])
        if len(train) < 15_000:
            raise ValueError(f"Insufficient training data for {month_start:%Y-%m}")
        features = ["lag_168h", "target_holiday", "lag_holiday"]
        train_frame = train[features].reset_index()
        train_frame["ds"] = train_frame["utc_timestamp"].dt.tz_localize(None)
        train_frame["y"] = train["actual_mw"].to_numpy()
        target_frame = target[features].reset_index()
        target_frame["ds"] = target_frame["utc_timestamp"].dt.tz_localize(None)
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            uncertainty_samples=0,
        )
        for feature in features:
            model.add_regressor(feature)
        model.fit(train_frame[["ds", "y", *features]])
        forecast = model.predict(target_frame[["ds", *features]])
        frames.append(pd.DataFrame({
            "utc_timestamp": target.index,
            "holiday_prophet_mw": forecast["yhat"].to_numpy(),
            "target_holiday": target["target_holiday"].to_numpy(),
            "lag_holiday": target["lag_holiday"].to_numpy(),
        }))
        print(f"Finished {month_start:%Y-%m}", flush=True)

    new = pd.concat(frames, ignore_index=True)
    old = pd.read_csv(COMPARISON, parse_dates=["utc_timestamp"])
    old = old.loc[old.utc_timestamp.dt.year == 2019]
    joined = old.merge(new, on="utc_timestamp", validate="one_to_one")
    joined.to_csv(OUT, index=False)
    flagged = (joined.target_holiday == 1) | (joined.lag_holiday == 1)
    rows = []
    for subset_name, subset in (("all_2019", joined), ("holiday_or_lag_holiday", joined.loc[flagged]), ("other_days", joined.loc[~flagged])):
        for model in ("same_hour_1_week_ago", "prophet_mw", "holiday_prophet_mw", "published_day_ahead"):
            error = subset[model] - subset["actual_mw"]
            rows.append((subset_name, model, len(subset), error.abs().mean(), error.mean()))

    report = """# Holiday-aware Prophet validation experiment

This experiment changes one thing in the existing monthly-refit Prophet model: it adds two known-at-forecast-time indicators for German nationwide public holidays, one for the target local date and one for the local date seven days earlier. It uses 2019 validation data only. State-specific holidays and bridge days are not covered.

| Slice | Method | Hours | MAE MW | Bias MW |
|---|---|---:|---:|---:|
"""
    for subset_name, model, count, mae, bias in rows:
        report += f"| {subset_name} | {model} | {count:,} | {mae:,.1f} | {bias:,.1f} |\n"
    report += "\nChoose future changes using validation only. Do not use these results as independent confirmation; the 2020 reference period has also since been inspected.\n"
    REPORT.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
