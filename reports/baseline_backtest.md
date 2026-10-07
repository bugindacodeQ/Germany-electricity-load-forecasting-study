# Day-ahead baseline backtest

## Decision and forecast definition

Forecast Germany's hourly load (MW) for the next UTC calendar day. We assume forecasts are issued at 12:00 UTC on the previous day. This is a study assumption, not a verified ENTSO-E submission time. The 48-hour and 168-hour lags are available before that cutoff for every target hour. The published day-ahead forecast is an external comparator; its precise issue time still needs verification.

## Evaluation

- Validation: 2019 (8,760 common hours). Choose the strongest simple baseline by MAE only here.
- Historical reference: January-September 2020 (6,576 common hours). This period was originally designated as the test but has since been inspected; it is not an untouched final test.
- Candidate baselines: same hour two days ago, same hour one week ago, and their equal-weight blend.
- Selected baseline on validation: **same_hour_1_week_ago**.
- Peak threshold: 69,055.3 MW, the 90th percentile of validation load. Peak MAE uses this fixed threshold in both periods.
- Forecast error = prediction minus actual. Positive bias means overforecasting.

| Period | Method | Hours | MAE MW | RMSE MW | Bias MW | Peak MAE MW |
|---|---|---:|---:|---:|---:|---:|
| validation_2019 | same_hour_2_days_ago | 8,760 | 7,376.7 | 9,741.8 | -5.2 | 7,200.2 |
| validation_2019 | same_hour_1_week_ago | 8,760 | 2,558.1 | 4,465.0 | 51.5 | 2,737.0 |
| validation_2019 | lag_blend | 8,760 | 4,386.6 | 5,710.9 | 23.2 | 4,577.3 |
| validation_2019 | published_day_ahead | 8,760 | 1,989.2 | 2,489.4 | -1,333.5 | 2,893.9 |
| historical_reference_2020 | same_hour_2_days_ago | 6,576 | 6,672.3 | 8,811.6 | -68.4 | 7,522.9 |
| historical_reference_2020 | same_hour_1_week_ago | 6,576 | 2,226.5 | 3,777.6 | -196.1 | 3,032.5 |
| historical_reference_2020 | lag_blend | 6,576 | 3,897.0 | 5,113.4 | -132.3 | 4,897.1 |
| historical_reference_2020 | published_day_ahead | 6,576 | 1,458.9 | 1,891.9 | 358.0 | 1,740.3 |

## Interpretation limits

This is a historical national-load backtest, not a measured saving for a company. 2020 includes unusual demand conditions, so the test is also a shift check. National load is not transferable directly to a plant or mini-grid. Before assessing financial value, obtain the actual operating decision, cost of over/underforecasting, and published forecast issue-time metadata. Before trying Prophet or another model, preserve these test dates and the common-hour comparison.
