# Feature availability at forecast issue time

## Forecast information boundary

Working assumption: issue a forecast at **12:00 UTC on D-1** for the next UTC day **D**, containing 24 target timestamps from D 00:00 through D 23:00 UTC. This is a project convention, not a verified operator schedule. The timing audit covers all 24-hour targets from 2017-01-01 through 2020-09-30.

## Feature audit

| Feature | Used in | Available by assumed cutoff? | Evidence and caveat |
|---|---|---|---|
| Target UTC timestamp; German local hour, weekday, weekend, annual cycle | Ridge, gradient boosting, neural network; Prophet calendar | Yes, by definition | Deterministic from the forecast target time. Local-time features account for Berlin clock changes, while the forecast horizon itself remains UTC. |
| German public holiday on target local date | ML models and holiday-aware heuristic | Yes, by calendar | Deterministic calendar feature. The project calendar is nationwide; state-specific holidays and bridge days are not represented. |
| German holiday flag for the same hour one week earlier | ML models / holiday rule | Yes, by calendar | Derived from target timestamp minus seven days. |
| Actual load lag 48 hours | Ridge, gradient boosting, neural network; naive comparator variants | Timestamp passes | Across the audited horizon, the lag is 13–36 hours before the assumed cutoff. Source publication latency and revisions are unknown, so actual value availability is not yet proven. |
| Actual load lag 168 hours | Prophet regressor, ML models, weekly seasonal naive | Timestamp passes | 133–156 hours before cutoff. Source publication latency and revisions are unknown. |
| Actual load lag 336 hours | ML models | Timestamp passes | 301–324 hours before cutoff. Source publication latency and revisions are unknown. |
| Scaler and target normalization parameters | Ridge and neural network | Yes, if trained correctly | Fit on training data only; the current benchmark code does this. |
| OPSD published day-ahead forecast | Comparator only | **Unverified** | The export has no issue/revision timestamp. Keep it as a historical reference, not a confirmed forecast available at the assumed cutoff. |
| Actual generation, realized weather, actual prices | EDA only; excluded from forecast models | No for this cutoff | These realized same-day quantities are not valid day-ahead predictors. Do not add them as features. |
| Day-ahead weather forecasts | Not currently used | Potentially, if archived vintages exist | No archive has been established for the study. Do not substitute realized weather for forecast weather. |

## Timing audit

The reproducible check in `scripts/audit_feature_availability.py` creates the next UTC day's 24 target hours and subtracts each lag. It found no lag timestamp at or after the assumed issue cutoff. It also found no missing source load values at those lag timestamps in the audited 2017–2020 horizons.

| Lag feature | Hours before cutoff, closest target hour | Hours before cutoff, earliest target hour | Timestamp violations |
|---|---:|---:|---:|
| 48-hour load lag | 13 | 36 | 0 |
| 168-hour load lag | 133 | 156 | 0 |
| 336-hour load lag | 301 | 324 | 0 |

This proves timestamp ordering only. The OPSD actual-load series does not provide row-level publication or revision times here, so we cannot verify that every historical value would have been in hand at the assumed cutoff or unrevised at that time. This is a remaining data-vintage limitation, not evidence of target leakage in the feature timestamps.

## Feature decision

Keep the existing calendar and lag features for the historical model study. Do not add realized weather, same-day generation, or prices. Add weather only if archived forecasts with issue times can be aligned to each forecast origin. Keep the published forecast comparator labeled as historical until vintages are recovered.

## Gate status

**Partially met.** The temporal ordering of candidate predictors passes, and learned preprocessing is training-only. Operational availability remains unverified for historical actual-load values, and the actual cutoff and UTC-versus-local delivery convention remain unconfirmed with an operator. Before describing this as an operationally validated feature set, obtain source publication/revision metadata or explicitly retain the caveat.
