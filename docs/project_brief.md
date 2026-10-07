# Project brief

> **Current evaluation status:** This brief contains the initial study plan. The 2017–2019 validation folds and January–September 2020 period have since been inspected. There is no untouched final test period; follow `docs/evaluation_protocol.md` for the current binding evaluation rules.

## Stakeholder and decision

Imagine a power-system planning team preparing a day-ahead demand schedule. It needs an hourly demand estimate and a clear view of uncertainty. The first question is whether a new forecasting method improves on a simple seasonal baseline and the published day-ahead forecast.

## Primary outcome

Forecast error in MW for each hour. Report MAE, bias, and error at high-demand hours. Compare the same timestamps across methods. Investigate whether errors cluster by hour, weekday, season, or demand level.

## Initial dataset slice

From `time_series_60min_singleindex.csv` in the project folder:

- `utc_timestamp`
- `DE_load_actual_entsoe_transparency`
- `DE_load_forecast_entsoe_transparency`

Start by auditing date coverage, missingness, duplicate timestamps, and time-zone handling. Select a contiguous period only after the audit. The published forecast is a benchmark, not a training feature for a model claiming to replace it.

## Evaluation rules

For any future generalization claim, reserve a later chronological holdout that is not used in model selection. Current 2017-2020 periods have been inspected. Define the day-ahead forecast cutoff before creating features. Calendar variables and older observations are reasonable inputs; observations from the forecasted day and actual same-hour renewable generation are unavailable at the cutoff. Check the published forecast's availability and timing before using it as a fair operational benchmark.

## Deliverables

1. Data audit and a clear account of exclusions.
2. Seasonal-naive baseline and published-forecast comparison.
3. One additional model only if it addresses a concrete error pattern.
4. A short decision memo: improvement, uncertainty, conditions where the approach fails, and what additional company data would be required to estimate financial value.
