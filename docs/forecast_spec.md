# Forecast specification

> **Status note:** This was the initial forecast plan. Subsequent model exploration inspected both 2017–2019 folds and the 2020 historical period. The 2020 period is not an untouched final test. The current binding protocol is `docs/evaluation_protocol.md`.

## Proposed user and decision

A power-system planner uses an hourly load forecast to prepare tomorrow's schedule. This public-data project tests forecast accuracy; it cannot establish operational savings without a firm's planning rules and costs.

## Target and horizon

- Target: German actual total load in MW, hourly, with timestamps interpreted in UTC.
- Horizon: all 24 hours of the next UTC calendar day.
- Assumed issue cutoff: 12:00 UTC on the previous day. Confirm the real operational cutoff with a stakeholder before calling this production-ready.
- Unit of evaluation: hourly forecast error on observed load.

## Information allowed at cutoff

Historical load whose timestamps precede the issue cutoff, calendar features, and external forecasts known before the cutoff. The baseline script uses load from 48 and 168 hours before each target hour. It does not use target-day actual load, actual renewable generation, or realized market prices.

## Backtest protocol

The original experiment used 2019 for validation and January-September 2020 as a final comparison period. Both have since been inspected; use 2020 only as a historical reference. Compare methods on common timestamps, with MAE as primary and RMSE, bias, and training-fold high-load MAE as supporting metrics.

The published forecast is a useful benchmark, but its exact issue time is not contained in this CSV. Treat the comparison as provisional until its availability relative to the assumed cutoff is verified. Any later model selection must use development folds only. Obtain a later chronological holdout and lock the model before scoring it once.

## Success condition

A future candidate is promising only if improvement repeats on a later untouched holdout and is operationally meaningful, particularly during high-demand hours. Even then, financial value requires a separate decision model with real operating costs.
