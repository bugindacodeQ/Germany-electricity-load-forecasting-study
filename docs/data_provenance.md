# Data provenance and forecast vintage

## Source and version

- Dataset: Open Power System Data (OPSD), Time series package, version `2020-10-06`, DOI [10.25832/time_series/2020-10-06](https://doi.org/10.25832/time_series/2020-10-06).
- File: `time_series_60min_singleindex.csv`, the hourly single-index extract.
- Primary source declared by OPSD: ENTSO-E Transparency Platform.
- The OPSD field definitions identify `DE_load_actual_entsoe_transparency` as Germany total load and `DE_load_forecast_entsoe_transparency` as Germany's day-ahead total-load forecast, both in MW.
- OPSD describes `utc_timestamp` as the start of each period in UTC. It also provides a Central European local timestamp with CET/CEST offsets.

References: [OPSD package README](https://data.open-power-system-data.org/time_series/2020-10-06/README.md), [OPSD field documentation](https://data.open-power-system-data.org/time_series/), [OPSD source mapping](https://github.com/Open-Power-System-Data/time_series/blob/master/input/sources.yml).

## Meaning of the load fields

ENTSO-E describes actual total load per bidding zone and market time unit as net generation minus exports plus imports minus energy absorbed by storage, including losses. This is a system-level balance quantity; it should not be described as a direct sum of customer meter readings. ENTSO-E describes the day-ahead forecast as the TSO's forecast of total load for each market time unit, prepared using historical load and forward-looking drivers including meteorological information.

Reference: [ENTSO-E Detailed Data Descriptions, total load and day-ahead forecast](https://www.entsoe.eu/fileadmin/user_upload/_library/resources/Transparency/02_MoP%20Ref02%20-%20DDD_V2R5.pdf).

## Local time and daylight saving

The CSV has a continuous UTC-hour index. Its CET/CEST field represents seasonal offset changes. For example, the local clock skips an hour in spring and repeats an hour in autumn, while UTC timestamps stay unique and hourly. The current analysis uses UTC for the target horizon and lag calculations. A real German day-ahead operation is organized around local market time, so the UTC-day horizon is a study convention and must be reviewed before making an operational claim. In particular, local delivery days can contain 23 or 25 hourly periods.

## File-level audit

Observed in `data/raw/time_series_60min_singleindex.csv`:

- 50,401 rows, from `2014-12-31 23:00 UTC` through `2020-09-30 23:00 UTC`.
- 50,401 unique, sorted timestamps; no missing hourly timestamps and no duplicates.
- Actual-load column: 1 missing value, at the first timestamp.
- Published day-ahead forecast column: 25 missing values: the first timestamp plus 24 consecutive hours from `2018-09-23 22:00 UTC` through `2018-09-24 21:00 UTC`.
- Do not impute the missing published forecast for benchmark scoring. Compare methods on common observed timestamps and report the excluded hours.

## Publication time and forecast revisions

ENTSO-E's data description sets a day-ahead forecast publication deadline of no later than two hours before the bidding-zone market gate closure, or D-1 12:00 local time where a gate-closure time does not apply. It also permits/mandates updates for major changes (defined there as at least a 10% change in a market time unit). The description says the forecast uses advance meteorological data and can change in shape and level.

The OPSD flat file preserves the target-period timestamp and forecast value, but not a per-value issue timestamp, revision timestamp, or archived vintage identifier. Therefore, the file alone cannot establish exactly what forecast a planner could see at our assumed 12:00 UTC cutoff, which revision is represented, or whether a historical reporting/methodology change caused the year-to-year bias shift. Treat the published forecast score as a historical-export reference, not a verified real-time comparator. Confirm which ENTSO-E rule version applied during each historical year before making a historical compliance claim.

## Step 2 outcome and remaining questions

**Confirmed:** source, dataset snapshot, target columns, units, broad system-level load definition, UTC interval labels, DST companion field, timeline continuity, duplicate status, and missing-value locations.

**Unresolved:** original issue/revision timestamps for forecast vintages; any historical changes in German load aggregation/definitions; and whether the final project should predict UTC calendar days or German local delivery days. These must be decided or explicitly caveated before freezing the final evaluation protocol.
