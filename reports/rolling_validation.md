# Expanding-window diagnostics before the previously inspected 2020 reference

Gradient boosting settings and features are held fixed from the prior benchmark. Each year is predicted from a model trained only on earlier years. This evaluates whether model skill repeats across historical years before 2020. The 2020 period has since been inspected and is not an untouched final test. Published forecast timing remains unverified.

| Year | Method | Hours | MAE MW | RMSE MW | Bias MW |
|---:|---|---:|---:|---:|---:|
| 2017 | same_hour_1_week_ago | 8,760 | 2,445.8 | 4,415.5 | 14.1 |
| 2017 | published_day_ahead | 8,760 | 1,395.8 | 1,802.3 | -449.0 |
| 2017 | gradient_boosting_mw | 8,760 | 1,422.0 | 1,974.6 | -254.2 |
| 2018 | same_hour_1_week_ago | 8,736 | 2,556.9 | 4,368.6 | -12.6 |
| 2018 | published_day_ahead | 8,736 | 1,577.1 | 1,999.0 | -474.6 |
| 2018 | gradient_boosting_mw | 8,736 | 1,580.1 | 2,133.4 | -226.5 |
| 2019 | same_hour_1_week_ago | 8,760 | 2,558.1 | 4,465.0 | 51.5 |
| 2019 | published_day_ahead | 8,760 | 1,989.2 | 2,489.4 | -1,333.5 |
| 2019 | gradient_boosting_mw | 8,760 | 1,404.4 | 1,913.6 | 146.1 |
