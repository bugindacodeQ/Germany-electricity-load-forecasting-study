# Standard ML and neural-network benchmark

> **Status note:** The January–September 2020 period below was originally called a test period, but has since been inspected during project work. Treat it as a historical reference, not an untouched final test.

All models use the same hourly target and comparison rows. Candidate inputs are known before the assumed 12:00 UTC previous-day cutoff: load 48, 168 and 336 hours before each target, local calendar cycles, and nationwide German holiday flags for target day and the prior-week reference day. Actual same-day generation and prices are excluded.

Ridge and histogram gradient boosting use fixed, untuned settings. The small two-hidden-layer PyTorch network uses 35 fixed training epochs and a fixed seed. Models fit on data through 2018 for 2019 validation, then refit on data through 2019 for January-September 2020 reference period. The holiday-aware policy was selected earlier using 2019. All methods below use the same nonmissing hours.

| Period | Method | Hours | MAE MW | RMSE MW | Bias MW | Peak MAE MW |
|---|---|---:|---:|---:|---:|---:|
| validation_2019 | lag_168h | 8,760 | 2,558.1 | 4,465.0 | 51.5 | 2,737.0 |
| validation_2019 | selected_policy_mw | 8,760 | 2,122.1 | 3,194.9 | -6.9 | 2,476.9 |
| validation_2019 | published_day_ahead | 8,760 | 1,989.2 | 2,489.4 | -1,333.5 | 2,893.9 |
| validation_2019 | ridge_mw | 8,760 | 2,080.1 | 3,014.5 | 21.6 | 2,502.4 |
| validation_2019 | gradient_boosting_mw | 8,760 | 1,404.4 | 1,913.6 | 146.1 | 1,387.7 |
| validation_2019 | neural_net_mw | 8,760 | 1,459.5 | 2,229.0 | 197.5 | 1,421.3 |
| historical_reference_2020 | lag_168h | 6,576 | 2,226.5 | 3,777.6 | -196.1 | 3,032.5 |
| historical_reference_2020 | selected_policy_mw | 6,576 | 1,898.0 | 2,830.8 | -163.4 | 2,646.4 |
| historical_reference_2020 | published_day_ahead | 6,576 | 1,458.9 | 1,891.9 | 358.0 | 1,740.3 |
| historical_reference_2020 | ridge_mw | 6,576 | 1,828.6 | 2,622.2 | 74.3 | 2,700.3 |
| historical_reference_2020 | gradient_boosting_mw | 6,576 | 1,415.3 | 1,960.9 | 319.4 | 1,348.6 |
| historical_reference_2020 | neural_net_mw | 6,576 | 1,599.6 | 2,150.6 | 887.6 | 1,219.9 |

The published forecast issue time is unverified. This is an accuracy comparison, not a savings claim.
