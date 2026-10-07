"""Check feature timestamps against the project's assumed day-ahead cutoff."""
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else Path(r"C:\Users\Hp\Desktop\GERMANY_POWER")
SOURCE = PROJECT / "data" / "raw" / "time_series_60min_singleindex.csv"
START = "2017-01-01"
END = "2020-09-30"
LAGS = (48, 168, 336)


def main() -> None:
    actual = pd.read_csv(
        SOURCE,
        usecols=["utc_timestamp", "DE_load_actual_entsoe_transparency"],
        parse_dates=["utc_timestamp"],
    ).set_index("utc_timestamp")["DE_load_actual_entsoe_transparency"]
    actual.index = pd.to_datetime(actual.index, utc=True)

    days = pd.date_range(START, END, freq="D", tz="UTC")
    target_hours = pd.DatetimeIndex([day + pd.Timedelta(hours=h) for day in days for h in range(24)])
    issue_cutoffs = pd.DatetimeIndex([day - pd.Timedelta(hours=12) for day in days for _ in range(24)])

    rows = []
    for lag in LAGS:
        feature_times = target_hours - pd.Timedelta(hours=lag)
        age_at_cutoff = issue_cutoffs - feature_times
        values = actual.reindex(feature_times)
        rows.append({
            "feature": f"actual_load_lag_{lag}h",
            "rows_checked": len(feature_times),
            "latest_feature_age_at_cutoff_h": age_at_cutoff.min().total_seconds() / 3600,
            "oldest_feature_age_at_cutoff_h": age_at_cutoff.max().total_seconds() / 3600,
            "timestamp_cutoff_violations": int((feature_times >= issue_cutoffs).sum()),
            "missing_source_values": int(values.isna().sum()),
            "temporal_check": "PASS" if (feature_times < issue_cutoffs).all() else "FAIL",
        })

    summary = pd.DataFrame(rows)
    if (summary.timestamp_cutoff_violations != 0).any():
        raise AssertionError("At least one lag timestamp is at or after the assumed issue cutoff")
    print("Assumption: issue at 12:00 UTC on D-1; target is UTC day D.")
    print(summary.to_string(index=False))
    print("\nCalendar and public-holiday flags are deterministic from the target timestamp/local date.")
    print("This checks timestamp ordering only; it does not prove when ENTSO-E published or revised actual load values.")


if __name__ == "__main__":
    main()
