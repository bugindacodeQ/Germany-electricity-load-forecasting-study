"""Export a typed, UTC-explicit hourly table for the Power BI report."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
SOURCE = ROOT / "data" / "raw" / "time_series_60min_singleindex.csv"
FOLD_PREDICTIONS = PROCESSED / "expanding_fold_predictions.csv"
OUTPUT = PROCESSED / "germany_powerbi_hourly.csv"

SOURCE_COLUMNS = {
    "DE_load_actual_entsoe_transparency": "actual_load_mw",
    "DE_load_forecast_entsoe_transparency": "published_forecast_mw",
    "DE_solar_generation_actual": "solar_generation_mw",
    "DE_wind_generation_actual": "wind_generation_mw",
    "DE_LU_price_day_ahead": "day_ahead_price_eur_mwh",
}
MODEL_COLUMNS = {
    "same_hour_48h": "same_hour_48h_forecast_mw",
    "same_hour_168h": "weekly_naive_forecast_mw",
    "ridge": "ridge_forecast_mw",
    "gradient_boosting": "gradient_boosting_forecast_mw",
    "neural_network": "neural_network_forecast_mw",
    "prophet": "prophet_forecast_mw",
}


def load_source() -> pd.DataFrame:
    if not SOURCE.is_file():
        raise SystemExit(f"Source CSV missing: {SOURCE}\nFollow the download instructions in README.md.")

    available = set(pd.read_csv(SOURCE, nrows=0).columns)
    required = {"utc_timestamp", "DE_load_actual_entsoe_transparency",
                "DE_load_forecast_entsoe_transparency"}
    missing = required - available
    if missing:
        raise SystemExit(f"Required OPSD columns missing: {', '.join(sorted(missing))}")
    columns = {source: target for source, target in SOURCE_COLUMNS.items() if source in available}
    frame = pd.read_csv(SOURCE, usecols=["utc_timestamp", *columns])
    frame = frame.rename(columns=columns)
    frame["utc_timestamp"] = pd.to_datetime(frame["utc_timestamp"], utc=True, errors="raise")
    if frame["utc_timestamp"].duplicated().any():
        raise ValueError("The OPSD source contains duplicate UTC timestamps.")
    return frame.sort_values("utc_timestamp").reset_index(drop=True)


def add_fold_predictions(frame: pd.DataFrame) -> pd.DataFrame:
    if not FOLD_PREDICTIONS.is_file():
        raise SystemExit(
            f"Fold predictions missing: {FOLD_PREDICTIONS}\n"
            "Run `python scripts/compare_models_folds.py` before exporting for Power BI."
        )

    selected = ["utc_timestamp", *MODEL_COLUMNS, "published_reference"]
    predictions = pd.read_csv(FOLD_PREDICTIONS, usecols=selected)
    predictions["utc_timestamp"] = pd.to_datetime(
        predictions["utc_timestamp"], utc=True, errors="raise"
    )
    predictions = predictions.rename(columns=MODEL_COLUMNS | {
        "published_reference": "published_forecast_backtest_mw"
    })
    if predictions["utc_timestamp"].duplicated().any():
        raise ValueError("Fold predictions contain duplicate UTC timestamps.")

    # Keep the raw-export reference as the primary published series. Check that
    # the benchmark file used the same value on its common timestamps.
    joined = frame.merge(predictions, on="utc_timestamp", how="left", validate="one_to_one")
    common = joined["published_forecast_backtest_mw"].notna()
    source_value = joined.loc[common, "published_forecast_mw"]
    fold_value = joined.loc[common, "published_forecast_backtest_mw"]
    if not source_value.isna().all() and not (source_value - fold_value).abs().le(1e-6).all():
        raise ValueError("Published forecast values differ between source and fold predictions.")
    joined = joined.drop(columns="published_forecast_backtest_mw")
    joined["has_backtest_prediction"] = joined["gradient_boosting_forecast_mw"].notna()
    return joined


def add_calendar_fields(frame: pd.DataFrame) -> pd.DataFrame:
    timestamp = frame["utc_timestamp"]
    berlin = timestamp.dt.tz_convert("Europe/Berlin")
    frame.insert(1, "date_utc", timestamp.dt.strftime("%Y-%m-%d"))
    frame.insert(2, "date_berlin", berlin.dt.strftime("%Y-%m-%d"))
    frame.insert(3, "year", timestamp.dt.year)
    frame.insert(4, "month_number", berlin.dt.month)
    frame.insert(5, "month_name", berlin.dt.strftime("%B"))
    frame.insert(6, "hour_utc", timestamp.dt.hour)
    frame.insert(7, "hour_berlin", berlin.dt.hour)
    frame.insert(8, "weekday_number_berlin", berlin.dt.dayofweek + 1)
    frame.insert(9, "weekday_name_berlin", berlin.dt.day_name())
    frame.insert(10, "utc_offset_berlin", berlin.dt.strftime("%z"))
    frame.insert(11, "country", "Germany")
    # Power BI Date/Time is timezone-naive; the column name and values are UTC.
    frame["utc_timestamp"] = timestamp.dt.strftime("%Y-%m-%d %H:%M:%S")
    frame["forecast_error_mw"] = frame["published_forecast_mw"] - frame["actual_load_mw"]
    frame["absolute_error_mw"] = frame["forecast_error_mw"].abs()
    return frame


def main() -> None:
    frame = load_source()
    frame = add_fold_predictions(frame)
    frame = add_calendar_fields(frame)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(frame):,} rows to {OUTPUT}")
    print(f"Rows with candidate fold predictions: {frame['has_backtest_prediction'].sum():,}")
    print("Rows with actual and published load:",
          frame[["actual_load_mw", "published_forecast_mw"]].notna().all(axis=1).sum())


if __name__ == "__main__":
    main()
