"""Audit timestamps and required load fields in the OPSD hourly CSV."""

import csv
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "time_series_60min_singleindex.csv"
REQUIRED = (
    "utc_timestamp",
    "DE_load_actual_entsoe_transparency",
    "DE_load_forecast_entsoe_transparency",
)


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        # The OPSD utc_timestamp field is UTC by definition.
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def main() -> None:
    if not DATA_FILE.is_file():
        raise SystemExit(f"Missing file: {DATA_FILE}\nDownload it using the link in README.md.")

    rows = 0
    first_timestamp = None
    last_timestamp = None
    missing = Counter()
    non_numeric = Counter()
    duplicates = 0
    missing_hour_slots = 0
    non_hourly_gaps = 0
    out_of_order = 0
    seen = set()
    previous = None

    with DATA_FILE.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        absent = [column for column in REQUIRED if column not in (reader.fieldnames or [])]
        if absent:
            raise SystemExit(f"Required columns absent: {', '.join(absent)}")

        for row in reader:
            rows += 1
            timestamp_text = row["utc_timestamp"]
            if not timestamp_text:
                missing["utc_timestamp"] += 1
                continue
            try:
                timestamp = parse_timestamp(timestamp_text)
            except ValueError as error:
                raise SystemExit(f"Invalid UTC timestamp on data row {rows}: {timestamp_text}") from error

            if first_timestamp is None:
                first_timestamp = timestamp
            last_timestamp = timestamp
            if timestamp in seen:
                duplicates += 1
            seen.add(timestamp)
            if previous is not None:
                delta = timestamp - previous
                if delta <= timedelta(0):
                    out_of_order += 1
                elif delta > timedelta(hours=1):
                    whole_hours, remainder = divmod(delta, timedelta(hours=1))
                    missing_hour_slots += max(0, whole_hours - 1)
                    if remainder:
                        non_hourly_gaps += 1
                elif delta != timedelta(hours=1):
                    non_hourly_gaps += 1
            previous = timestamp

            for column in REQUIRED[1:]:
                value = row[column]
                if value is None or not value.strip():
                    missing[column] += 1
                else:
                    try:
                        float(value)
                    except ValueError:
                        non_numeric[column] += 1

    print(f"Rows: {rows:,}")
    print(f"First timestamp: {first_timestamp}")
    print(f"Last timestamp: {last_timestamp}")
    print(f"Unique timestamps: {len(seen):,}")
    print(f"Duplicate timestamps: {duplicates:,}")
    print(f"Out-of-order timestamp transitions: {out_of_order:,}")
    print(f"Missing hourly slots between rows: {missing_hour_slots:,}")
    print(f"Non-hourly timestamp gaps: {non_hourly_gaps:,}")
    for column in REQUIRED:
        print(f"{column}: missing={missing[column]:,}, non_numeric={non_numeric[column]:,}")


if __name__ == "__main__":
    main()
