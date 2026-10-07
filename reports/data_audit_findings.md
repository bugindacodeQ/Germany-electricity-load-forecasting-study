# Data audit

Run `python scripts/audit_data.py` from the project root to check the source file. The detailed provenance and interval audit is in [data_provenance.md](../docs/data_provenance.md).

## Findings

- 50,401 hourly rows, `2014-12-31 23:00 UTC` through `2020-09-30 23:00 UTC`.
- Complete, sorted UTC hourly index; 0 missing timestamps and 0 duplicates.
- Actual load missing at the first timestamp only (1 row).
- Published day-ahead forecast missing at the first timestamp and for a continuous 24-hour block (`2018-09-23 22:00 UTC` through `2018-09-24 21:00 UTC`).
- Do not fill missing forecast values for benchmark comparisons. Keep comparisons on common complete hours.

See the provenance document for load definitions, DST, and forecast-vintage limits.
