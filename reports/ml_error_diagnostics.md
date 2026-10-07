# Error diagnostics by time and demand level

> **Status note:** 2020 slices below are post-hoc diagnostics for a previously inspected historical reference period. They are not new model-selection evidence or a clean final test.

Positive MAE gain means gradient boosting has lower absolute error than the published forecast. These slices are diagnostic, not new model-selection evidence. Grouping uses German local time. The 2020 scored-period cutoff was defined in UTC, so its final local month contains only the last two hours of October.

Across 274 test days, mean daily hourly-MAE gain was 43.6 MW. A paired day-level bootstrap (10,000 resamples, seed 42) gives a 95% interval of -66.0 to 143.2 MW; it includes zero. Gradient boosting had lower daily MAE on 154 of 274 days.

## Monthly results

| period | local_month | hours | gradient_boosting_mae_mw | published_mae_mw | mae_gain_mw | gradient_boosting_bias_mw | published_bias_mw |
| --- | --- | --- | --- | --- | --- | --- | --- |
| historical_reference_2020 | 2020-01 | 743 | 1382.5 | 1864.1 | 481.7 | -311.4 | -529.0 |
| historical_reference_2020 | 2020-02 | 696 | 1003.7 | 1293.7 | 290.0 | 99.8 | 291.0 |
| historical_reference_2020 | 2020-03 | 743 | 1834.4 | 2188.0 | 353.6 | 818.3 | 1564.4 |
| historical_reference_2020 | 2020-04 | 720 | 1958.8 | 2001.5 | 42.6 | 915.2 | 1847.1 |
| historical_reference_2020 | 2020-05 | 744 | 1518.2 | 1667.9 | 149.7 | 547.4 | 1268.3 |
| historical_reference_2020 | 2020-06 | 720 | 1572.7 | 1045.8 | -526.9 | 586.1 | 488.1 |
| historical_reference_2020 | 2020-07 | 744 | 963.0 | 801.2 | -161.7 | 265.6 | -247.2 |
| historical_reference_2020 | 2020-08 | 744 | 1515.7 | 1177.0 | -338.7 | 12.7 | -544.0 |
| historical_reference_2020 | 2020-09 | 720 | 972.9 | 1076.6 | 103.7 | -54.8 | -907.3 |
| historical_reference_2020 | 2020-10 | 2 | 608.1 | 370.5 | -237.6 | -608.1 | -370.5 |
| validation_2019 | 2019-01 | 743 | 1496.2 | 2523.7 | 1027.5 | -524.2 | -2181.8 |
| validation_2019 | 2019-02 | 672 | 1293.1 | 1464.9 | 171.7 | 718.7 | -827.1 |
| validation_2019 | 2019-03 | 743 | 1561.0 | 1773.8 | 212.9 | -267.2 | -1534.5 |
| validation_2019 | 2019-04 | 720 | 1704.7 | 2684.5 | 979.8 | 337.2 | -2160.1 |
| validation_2019 | 2019-05 | 744 | 1529.8 | 3241.4 | 1711.5 | -292.5 | -3148.0 |
| validation_2019 | 2019-06 | 720 | 1837.6 | 2864.2 | 1026.6 | 51.7 | -2769.2 |
| validation_2019 | 2019-07 | 744 | 913.8 | 1130.7 | 216.9 | 153.1 | -293.0 |
| validation_2019 | 2019-08 | 744 | 1240.0 | 1291.8 | 51.8 | 301.5 | -436.3 |
| validation_2019 | 2019-09 | 720 | 1105.9 | 1257.6 | 151.6 | 115.2 | -447.6 |
| validation_2019 | 2019-10 | 745 | 1219.4 | 1626.2 | 406.8 | 172.3 | -1010.8 |
| validation_2019 | 2019-11 | 720 | 1184.4 | 2008.4 | 824.0 | 273.3 | -1478.2 |
| validation_2019 | 2019-12 | 744 | 1762.7 | 1980.0 | 217.2 | 776.6 | 277.2 |
| validation_2019 | 2020-01 | 1 | 1605.2 | 3137.0 | 1531.8 | -1605.2 | 3137.0 |

Weakest 2020 months (negative gain favors the published forecast): 2020-06 (-527 MW), 2020-08 (-339 MW), 2020-10 (-238 MW).

## Test-period hour of day

| local_hour | hours | gradient_boosting_mae_mw | published_mae_mw | mae_gain_mw | gradient_boosting_bias_mw | published_bias_mw |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 274 | 1132.4 | 1271.5 | 139.1 | 122.8 | 511.4 |
| 1 | 275 | 1193.1 | 1279.0 | 85.9 | 341.5 | 267.2 |
| 2 | 273 | 1241.6 | 1194.5 | -47.0 | 603.4 | 186.6 |
| 3 | 274 | 1262.3 | 1214.5 | -47.8 | 602.8 | 187.1 |
| 4 | 274 | 1185.4 | 1244.7 | 59.3 | 419.4 | 160.6 |
| 5 | 274 | 1265.7 | 1338.0 | 72.3 | 236.1 | 60.3 |
| 6 | 274 | 1514.3 | 1553.2 | 38.9 | 740.7 | 387.9 |
| 7 | 274 | 1566.6 | 1616.6 | 49.9 | 407.0 | 527.1 |
| 8 | 274 | 1492.3 | 1607.9 | 115.6 | 183.6 | 428.7 |
| 9 | 274 | 1537.3 | 1581.7 | 44.4 | 197.3 | 358.4 |
| 10 | 274 | 1514.6 | 1571.9 | 57.3 | 193.0 | 265.1 |
| 11 | 274 | 1624.4 | 1610.3 | -14.1 | 308.7 | 193.0 |
| 12 | 274 | 1599.9 | 1555.5 | -44.4 | 331.1 | 27.4 |
| 13 | 274 | 1650.0 | 1613.1 | -36.8 | 302.1 | 129.2 |
| 14 | 274 | 1636.5 | 1607.4 | -29.1 | 262.6 | 172.6 |
| 15 | 274 | 1656.3 | 1593.4 | -62.9 | 405.8 | 274.3 |
| 16 | 274 | 1769.5 | 1636.6 | -132.9 | 601.4 | 367.9 |
| 17 | 274 | 1645.3 | 1690.5 | 45.2 | 449.5 | 352.0 |
| 18 | 274 | 1500.0 | 1552.2 | 52.2 | 367.7 | 570.0 |
| 19 | 274 | 1358.9 | 1397.2 | 38.4 | 93.4 | 594.0 |
| 20 | 274 | 1238.9 | 1336.0 | 97.2 | 85.0 | 544.1 |
| 21 | 274 | 1184.3 | 1282.2 | 97.9 | 104.2 | 498.9 |
| 22 | 274 | 1075.2 | 1301.8 | 226.6 | 115.9 | 732.3 |
| 23 | 274 | 1121.8 | 1363.5 | 241.7 | 192.7 | 795.3 |

## Test-period weekday

| local_weekday | hours | gradient_boosting_mae_mw | published_mae_mw | mae_gain_mw | gradient_boosting_bias_mw | published_bias_mw |
| --- | --- | --- | --- | --- | --- | --- |
| Friday | 936 | 1590.3 | 1542.6 | -47.8 | 313.8 | 740.3 |
| Monday | 936 | 1387.6 | 1496.6 | 109.0 | 269.8 | 71.6 |
| Saturday | 936 | 1114.1 | 1264.4 | 150.4 | 11.0 | 785.5 |
| Sunday | 935 | 1218.0 | 1330.7 | 112.8 | 134.1 | 526.1 |
| Thursday | 938 | 1653.4 | 1486.7 | -166.7 | 571.1 | 277.9 |
| Tuesday | 936 | 1581.5 | 1620.3 | 38.8 | 358.1 | -1.8 |
| Wednesday | 959 | 1362.6 | 1470.6 | 108.0 | 571.1 | 112.8 |

## Test-period demand decile

Deciles are calculated within the scored reference period. They are for error diagnosis, not forecast-time features.

| demand_decile | hours | gradient_boosting_mae_mw | published_mae_mw | mae_gain_mw | gradient_boosting_bias_mw | published_bias_mw |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 913 | 1397.6 | 1311.0 | -86.6 | 942.1 | 707.6 |
| 2 | 782 | 1230.6 | 1335.6 | 105.0 | 452.5 | 559.6 |
| 3 | 620 | 1206.8 | 1343.6 | 136.8 | 151.9 | 682.0 |
| 4 | 598 | 1388.4 | 1380.1 | -8.3 | 269.6 | 615.0 |
| 5 | 642 | 1389.5 | 1610.3 | 220.7 | 128.2 | 660.3 |
| 6 | 754 | 1566.9 | 1564.6 | -2.4 | 343.5 | 920.2 |
| 7 | 837 | 1644.0 | 1483.7 | -160.3 | 487.3 | 437.3 |
| 8 | 601 | 1514.3 | 1432.3 | -82.0 | 306.1 | -352.7 |
| 9 | 350 | 1400.8 | 1612.6 | 211.9 | -33.2 | -652.3 |
| 10 | 479 | 1336.3 | 1698.3 | 362.0 | -606.0 | -1176.6 |

## Readout

The headline MAE difference is small and varies by month, hour, and load range. Neither forecast dominates in every slice. Do not tune to these 2020 slices. Any further model changes based on the already-inspected 2017-2019 folds are also exploratory; reserve a later unseen holdout for independent confirmation. The published forecast's issue time remains unverified, so its comparison is still provisional operationally.
