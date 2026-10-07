# Why did the model comparison change?

> **Status note:** All 2020 results referenced here have been inspected; 2020 is a historical reference period, not an untouched test.

## Findings from the backtests

Gradient boosting's MAE stayed in a relatively narrow range: 1,422 MW in 2017, 1,580 MW in 2018, 1,404 MW in 2019, and 1,415 MW in the January–September 2020 reference period.

The published forecast changed more. Its MAE was 1,396 MW in 2017, 1,577 MW in 2018, 1,989 MW in 2019, and 1,459 MW in the 2020 reference period. Its mean error (forecast minus actual) was -449, -475, -1,334, and +358 MW in those periods. This points to a change in the benchmark error profile as the main reason the relative ranking changed. The backtests alone do not establish why the published forecast shifted.

The 2020 result also varies by month. Gradient boosting's MAE was better in January–May and September, while the published forecast was better in June–August. Demand changed during 2020; for example, average actual load in April and May was much lower than winter load. The current candidate models use historical load and calendar features, but no weather forecast or other contemporaneous demand drivers.

## What the source documentation establishes

OPSD maps `DE_load_forecast_entsoe_transparency` to ENTSO-E's day-ahead total-load forecast and obtains it from monthly ENTSO-E Transparency Platform exports. Its documented source fields contain target timestamp, resolution, area, and value; the harmonized CSV has no forecast issue-time or revision-time field. [OPSD field documentation](https://data.open-power-system-data.org/time_series/2020-10-06/README.md) · [OPSD source mapping](https://github.com/Open-Power-System-Data/time_series/blob/master/input/sources.yml)

ENTSO-E's data description says the day-ahead forecast is supplied by TSOs (with TSOs/DSOs as primary owners), should be published no later than two hours before day-ahead market gate closure, or by D-1 12:00 local time when a gate closure time does not apply, and must be updated after a major change of at least 10% in a market time unit. [ENTSO-E Detailed Data Descriptions, section 3.2](https://www.entsoe.eu/fileadmin/user_upload/_library/resources/Transparency/02_MoP%20Ref02%20-%20DDD_V2R5.pdf)

This establishes a regulatory publication deadline and an update rule. It does **not** tell us which version of each historical hourly forecast OPSD retained, the actual issue timestamp, whether a later revision is represented, or whether the forecast method changed between years. The comparison therefore measures against the forecast values in this historical export; it is not yet a strict real-time backtest against a known vintage.

## Most plausible explanation, with limits

The measured ranking change is mostly due to the published forecast's errors worsening in 2019 and improving again in 2020, while gradient boosting's aggregate MAE remains fairly stable. The 2020 seasonal reversals suggest that conditions and forecast performance vary within the year. Missing weather inputs are one plausible source of residual error for our model, but this dataset cannot prove that weather caused the difference. COVID-era changes, holidays, calendar effects, source revisions, changes in reporting, and load-definition changes also need investigation.

## Next evidence to obtain

1. Forecast vintages or publication timestamps for ENTSO-E day-ahead load forecasts, if available, to compare the same information cutoff.
2. Historical weather observations and, ideally, archived day-ahead weather forecasts. Observations support error diagnosis; only archived forecasts are valid model inputs for a day-ahead backtest.
3. Documentation of any historical changes to Germany's load definition, aggregation, or ENTSO-E reporting.

Until those checks are possible, present the published forecast as a historical reference series, label the 12:00 UTC cutoff as a project assumption, and avoid attributing the year-to-year change to one cause.
