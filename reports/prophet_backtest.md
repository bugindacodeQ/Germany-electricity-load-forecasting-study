# Prophet day-ahead backtest

Prophet is refitted at the beginning of each month on the previous two years of hourly data. It predicts every hour of that month using calendar seasonality and load from the same hour one week earlier. That lag is known before an assumed 12:00 UTC cutoff on the previous day. The model parameters remain fixed within each month; the lag input updates as historical observations become available. No forecast-month actual load enters model fitting until a later month's refit.

The original split used 2019 for validation and January-September 2020 as a final test. Both periods have since been inspected; 2020 is a historical reference, not an untouched test. All methods below use identical hours. Peak demand is defined using the validation period 90th percentile. The published forecast issue time remains unverified.

| Period | Method | Hours | MAE MW | RMSE MW | Bias MW | Peak MAE MW |
|---|---|---:|---:|---:|---:|---:|
| validation_2019 | same_hour_1_week_ago | 8,760 | 2,558.1 | 4,465.0 | 51.5 | 2,737.0 |
| validation_2019 | published_day_ahead | 8,760 | 1,989.2 | 2,489.4 | -1,333.5 | 2,893.9 |
| validation_2019 | prophet_mw | 8,760 | 2,797.4 | 3,950.6 | -527.8 | 3,760.5 |
| historical_reference_2020 | same_hour_1_week_ago | 6,576 | 2,226.5 | 3,777.6 | -196.1 | 3,032.5 |
| historical_reference_2020 | published_day_ahead | 6,576 | 1,458.9 | 1,891.9 | 358.0 | 1,740.3 |
| historical_reference_2020 | prophet_mw | 6,576 | 2,497.8 | 3,522.0 | -461.1 | 4,521.5 |

## Limits

The monthly refit schedule is a computational and operational choice; it is not a daily refit. The 2020 reference period includes demand shifts during the COVID-19 pandemic. These aggregate grid results do not measure a specific company's savings. A separate cost model and operational data would be needed for that claim.
