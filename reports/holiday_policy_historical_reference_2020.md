# Holiday-aware policy: 2020 historical reference

The policy was selected using 2019 validation results: holiday-aware Prophet when the target local date or same-hour prior-week local date is a German nationwide holiday; otherwise use the same-hour prior-week forecast. This file reports the previously inspected January-September 2020 historical reference, not an untouched final test. State-specific holidays and bridge days are not covered. All methods use the same hours.

| Slice | Method | Hours | MAE MW | Bias MW |
|---|---|---:|---:|---:|
| all_2020_reference | same_hour_1_week_ago | 6,576 | 2,226.5 | -196.1 |
| all_2020_reference | prophet_mw | 6,576 | 2,497.8 | -461.1 |
| all_2020_reference | holiday_prophet_mw | 6,576 | 2,023.2 | -517.6 |
| all_2020_reference | selected_policy_mw | 6,576 | 1,898.0 | -163.4 |
| all_2020_reference | published_day_ahead | 6,576 | 1,458.9 | 358.0 |
| holiday_or_lag_holiday | same_hour_1_week_ago | 311 | 10,993.9 | -1,858.2 |
| holiday_or_lag_holiday | prophet_mw | 311 | 7,978.5 | 1,231.6 |
| holiday_or_lag_holiday | holiday_prophet_mw | 311 | 4,048.0 | -1,166.3 |
| holiday_or_lag_holiday | selected_policy_mw | 311 | 4,048.0 | -1,166.3 |
| holiday_or_lag_holiday | published_day_ahead | 311 | 2,369.5 | 1,610.2 |
| other_days | same_hour_1_week_ago | 6,265 | 1,791.3 | -113.6 |
| other_days | prophet_mw | 6,265 | 2,225.7 | -545.1 |
| other_days | holiday_prophet_mw | 6,265 | 1,922.7 | -485.4 |
| other_days | selected_policy_mw | 6,265 | 1,791.3 | -113.6 |
| other_days | published_day_ahead | 6,265 | 1,413.7 | 295.8 |

The published forecast's exact issue time is not verified. The result measures forecast accuracy, not monetary value.
