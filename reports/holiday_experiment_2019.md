# Holiday-aware Prophet validation experiment

This experiment changes one thing in the existing monthly-refit Prophet model: it adds two known-at-forecast-time indicators for German nationwide public holidays, one for the target local date and one for the local date seven days earlier. It uses 2019 validation data only. State-specific holidays and bridge days are not covered.

| Slice | Method | Hours | MAE MW | Bias MW |
|---|---|---:|---:|---:|
| all_2019 | same_hour_1_week_ago | 8,760 | 2,558.1 | 51.5 |
| all_2019 | prophet_mw | 8,760 | 2,797.4 | -527.8 |
| all_2019 | holiday_prophet_mw | 8,760 | 2,405.3 | -525.0 |
| all_2019 | published_day_ahead | 8,760 | 1,989.2 | -1,333.5 |
| holiday_or_lag_holiday | same_hour_1_week_ago | 408 | 13,799.9 | 47.1 |
| holiday_or_lag_holiday | prophet_mw | 408 | 9,760.6 | 2,218.6 |
| holiday_or_lag_holiday | holiday_prophet_mw | 408 | 4,437.6 | -1,207.7 |
| holiday_or_lag_holiday | published_day_ahead | 408 | 2,248.2 | -1,273.5 |
| other_days | same_hour_1_week_ago | 8,352 | 2,009.0 | 51.8 |
| other_days | prophet_mw | 8,352 | 2,457.3 | -661.9 |
| other_days | holiday_prophet_mw | 8,352 | 2,306.0 | -491.7 |
| other_days | published_day_ahead | 8,352 | 1,976.6 | -1,336.4 |

Choose future changes using validation only. Do not claim a gain on the 2020 test from these results.
