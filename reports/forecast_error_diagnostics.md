# Error patterns and historical load shifts

This is descriptive diagnosis. The 2017–2019 validation folds were already inspected and remain development evidence; 2020 is a previously viewed reference period. Do not use these slices to tune and then present the same periods as independent confirmation. Grouping uses Europe/Berlin local time. Load deciles are calculated within each scored year and are diagnostic only.

## Annual forecast error

| year | model | hours | mae_mw | rmse_mw | bias_mw |
|---|---|---|---|---|---|
| 2017 | gradient_boosting | 8,760 | 1,422.0 | 1,974.6 | -254.2 |
| 2017 | published_reference | 8,760 | 1,395.8 | 1,802.3 | -449.0 |
| 2017 | weekly_naive | 8,760 | 2,445.8 | 4,415.5 | 14.2 |
| 2018 | gradient_boosting | 8,736 | 1,580.1 | 2,133.4 | -226.5 |
| 2018 | published_reference | 8,736 | 1,577.1 | 1,999.0 | -474.6 |
| 2018 | weekly_naive | 8,736 | 2,556.8 | 4,368.6 | -12.6 |
| 2019 | gradient_boosting | 8,760 | 1,404.4 | 1,913.6 | 146.1 |
| 2019 | published_reference | 8,760 | 1,989.2 | 2,489.4 | -1,333.5 |
| 2019 | weekly_naive | 8,760 | 2,558.2 | 4,465.0 | 51.5 |
| 2020 | gradient_boosting | 6,576 | 1,415.3 | 1,960.9 | 319.4 |
| 2020 | published_reference | 6,576 | 1,458.9 | 1,891.9 | 358.0 |
| 2020 | weekly_naive | 6,576 | 2,226.5 | 3,777.6 | -196.1 |

Positive bias means forecast minus actual (overforecast); negative bias means underforecast.

## Gradient boosting by local season

| year | season | hours | mae_mw | bias_mw |
|---|---|---|---|---|
| 2017 | Autumn | 2,185 | 1,271.0 | -310.0 |
| 2017 | Spring | 2,207 | 1,529.5 | -222.5 |
| 2017 | Summer | 2,208 | 1,104.4 | 50.0 |
| 2017 | Winter | 2,160 | 1,789.7 | -541.2 |
| 2018 | Autumn | 2,161 | 1,481.2 | -152.5 |
| 2018 | Spring | 2,207 | 1,972.2 | -169.9 |
| 2018 | Summer | 2,208 | 1,268.2 | -229.3 |
| 2018 | Winter | 2,160 | 1,597.3 | -355.4 |
| 2019 | Autumn | 2,185 | 1,170.5 | 186.8 |
| 2019 | Spring | 2,207 | 1,597.4 | -78.5 |
| 2019 | Summer | 2,208 | 1,325.0 | 170.1 |
| 2019 | Winter | 2,160 | 1,524.9 | 310.0 |
| 2020 | Autumn | 722 | 971.9 | -56.4 |
| 2020 | Spring | 2,207 | 1,768.4 | 758.6 |
| 2020 | Summer | 2,208 | 1,348.0 | 284.9 |
| 2020 | Winter | 1,439 | 1,199.3 | -112.5 |

## Gradient boosting by local hour

| year | local_hour | hours | mae_mw | bias_mw |
|---|---|---|---|---|
| 2017 | 0 | 365 | 1,245.2 | -88.6 |
| 2017 | 1 | 365 | 1,201.5 | -43.2 |
| 2017 | 2 | 365 | 1,146.3 | -77.8 |
| 2017 | 3 | 365 | 1,154.0 | -68.0 |
| 2017 | 4 | 365 | 1,164.4 | -65.4 |
| 2017 | 5 | 365 | 1,308.8 | -138.6 |
| 2017 | 6 | 365 | 1,362.1 | -275.9 |
| 2017 | 7 | 365 | 1,434.9 | -266.8 |
| 2017 | 8 | 365 | 1,475.2 | -424.1 |
| 2017 | 9 | 365 | 1,375.0 | -409.2 |
| 2017 | 10 | 365 | 1,487.8 | -494.3 |
| 2017 | 11 | 365 | 1,608.7 | -640.9 |
| 2017 | 12 | 365 | 1,594.0 | -558.6 |
| 2017 | 13 | 365 | 1,611.8 | -410.6 |
| 2017 | 14 | 365 | 1,641.1 | -253.0 |
| 2017 | 15 | 365 | 1,602.3 | -217.6 |
| 2017 | 16 | 365 | 1,616.3 | -213.9 |
| 2017 | 17 | 365 | 1,670.9 | -399.2 |
| 2017 | 18 | 365 | 1,586.6 | -427.4 |
| 2017 | 19 | 365 | 1,468.4 | -344.6 |
| 2017 | 20 | 365 | 1,330.9 | -117.0 |
| 2017 | 21 | 365 | 1,340.0 | -65.9 |
| 2017 | 22 | 365 | 1,355.0 | -71.5 |
| 2017 | 23 | 365 | 1,347.5 | -29.3 |
| 2018 | 0 | 364 | 1,597.7 | -43.9 |
| 2018 | 1 | 364 | 1,554.2 | -175.0 |
| 2018 | 2 | 364 | 1,527.9 | -148.7 |
| 2018 | 3 | 364 | 1,482.5 | -154.4 |
| 2018 | 4 | 364 | 1,477.2 | -132.4 |
| 2018 | 5 | 364 | 1,558.2 | -185.1 |
| 2018 | 6 | 364 | 1,540.5 | -180.6 |
| 2018 | 7 | 364 | 1,500.9 | -228.9 |
| 2018 | 8 | 364 | 1,583.8 | -315.8 |
| 2018 | 9 | 364 | 1,537.6 | -345.5 |
| 2018 | 10 | 364 | 1,600.4 | -350.7 |
| 2018 | 11 | 364 | 1,661.1 | -384.7 |
| 2018 | 12 | 364 | 1,673.4 | -349.5 |
| 2018 | 13 | 364 | 1,655.5 | -309.2 |
| 2018 | 14 | 364 | 1,697.5 | -229.4 |
| 2018 | 15 | 364 | 1,712.5 | -198.3 |
| 2018 | 16 | 364 | 1,648.1 | -177.1 |
| 2018 | 17 | 364 | 1,664.3 | -281.3 |
| 2018 | 18 | 364 | 1,615.9 | -329.3 |
| 2018 | 19 | 364 | 1,550.7 | -361.3 |
| 2018 | 20 | 364 | 1,489.7 | -236.4 |
| 2018 | 21 | 364 | 1,462.7 | -163.5 |
| 2018 | 22 | 364 | 1,515.3 | -129.1 |
| 2018 | 23 | 364 | 1,615.5 | -25.4 |
| 2019 | 0 | 365 | 1,441.1 | 14.1 |
| 2019 | 1 | 365 | 1,370.8 | 64.4 |
| 2019 | 2 | 365 | 1,349.1 | 109.0 |
| 2019 | 3 | 365 | 1,329.0 | 90.4 |
| 2019 | 4 | 365 | 1,283.5 | 75.6 |
| 2019 | 5 | 365 | 1,359.2 | 4.2 |
| 2019 | 6 | 365 | 1,485.1 | 183.9 |
| 2019 | 7 | 365 | 1,444.9 | 132.7 |
| 2019 | 8 | 365 | 1,356.5 | 84.8 |
| 2019 | 9 | 365 | 1,333.0 | 133.8 |
| 2019 | 10 | 365 | 1,408.0 | 191.8 |
| 2019 | 11 | 365 | 1,460.6 | 184.5 |
| 2019 | 12 | 365 | 1,427.8 | 230.2 |
| 2019 | 13 | 365 | 1,514.5 | 251.0 |
| 2019 | 14 | 365 | 1,569.5 | 257.5 |
| 2019 | 15 | 365 | 1,604.1 | 266.6 |
| 2019 | 16 | 365 | 1,567.9 | 324.4 |
| 2019 | 17 | 365 | 1,501.4 | 201.7 |
| 2019 | 18 | 365 | 1,364.8 | 98.8 |
| 2019 | 19 | 365 | 1,316.6 | 92.8 |
| 2019 | 20 | 365 | 1,262.9 | 95.9 |
| 2019 | 21 | 365 | 1,278.5 | 130.6 |
| 2019 | 22 | 365 | 1,333.7 | 139.7 |
| 2019 | 23 | 365 | 1,342.1 | 148.4 |
| 2020 | 0 | 274 | 1,132.4 | 122.8 |
| 2020 | 1 | 275 | 1,193.1 | 341.5 |
| 2020 | 2 | 273 | 1,241.6 | 603.4 |
| 2020 | 3 | 274 | 1,262.3 | 602.8 |
| 2020 | 4 | 274 | 1,185.4 | 419.4 |
| 2020 | 5 | 274 | 1,265.7 | 236.1 |
| 2020 | 6 | 274 | 1,514.3 | 740.7 |
| 2020 | 7 | 274 | 1,566.6 | 407.0 |
| 2020 | 8 | 274 | 1,492.3 | 183.6 |
| 2020 | 9 | 274 | 1,537.3 | 197.3 |
| 2020 | 10 | 274 | 1,514.6 | 193.1 |
| 2020 | 11 | 274 | 1,624.4 | 308.7 |
| 2020 | 12 | 274 | 1,599.9 | 331.1 |
| 2020 | 13 | 274 | 1,650.0 | 302.1 |
| 2020 | 14 | 274 | 1,636.5 | 262.6 |
| 2020 | 15 | 274 | 1,656.3 | 405.8 |
| 2020 | 16 | 274 | 1,769.5 | 601.4 |
| 2020 | 17 | 274 | 1,645.3 | 449.5 |
| 2020 | 18 | 274 | 1,500.0 | 367.7 |
| 2020 | 19 | 274 | 1,358.9 | 93.4 |
| 2020 | 20 | 274 | 1,238.8 | 85.0 |
| 2020 | 21 | 274 | 1,184.3 | 104.2 |
| 2020 | 22 | 274 | 1,075.2 | 115.9 |
| 2020 | 23 | 274 | 1,121.8 | 192.7 |

## Gradient boosting by weekday

| year | weekday | hours | mae_mw | bias_mw |
|---|---|---|---|---|
| 2017 | Friday | 1,248 | 1,324.0 | -197.9 |
| 2017 | Monday | 1,249 | 1,714.4 | -326.2 |
| 2017 | Saturday | 1,248 | 1,284.9 | -28.2 |
| 2017 | Sunday | 1,271 | 1,341.7 | 236.8 |
| 2017 | Thursday | 1,248 | 1,437.4 | -392.4 |
| 2017 | Tuesday | 1,248 | 1,529.8 | -779.3 |
| 2017 | Wednesday | 1,248 | 1,323.2 | -301.3 |
| 2018 | Friday | 1,248 | 1,500.6 | -176.4 |
| 2018 | Monday | 1,247 | 1,835.6 | -361.9 |
| 2018 | Saturday | 1,248 | 1,407.8 | -126.1 |
| 2018 | Sunday | 1,248 | 1,351.9 | -114.4 |
| 2018 | Thursday | 1,248 | 1,605.0 | -154.8 |
| 2018 | Tuesday | 1,249 | 1,747.5 | -417.6 |
| 2018 | Wednesday | 1,248 | 1,612.6 | -234.0 |
| 2019 | Friday | 1,248 | 1,717.2 | 428.8 |
| 2019 | Monday | 1,248 | 1,422.7 | 37.7 |
| 2019 | Saturday | 1,248 | 1,277.4 | 71.3 |
| 2019 | Sunday | 1,248 | 1,232.3 | 161.3 |
| 2019 | Thursday | 1,248 | 1,479.7 | 180.2 |
| 2019 | Tuesday | 1,271 | 1,373.4 | 11.5 |
| 2019 | Wednesday | 1,249 | 1,328.5 | 134.5 |
| 2020 | Friday | 936 | 1,590.3 | 313.8 |
| 2020 | Monday | 936 | 1,387.6 | 269.8 |
| 2020 | Saturday | 936 | 1,114.1 | 11.0 |
| 2020 | Sunday | 935 | 1,218.0 | 134.2 |
| 2020 | Thursday | 938 | 1,653.4 | 571.1 |
| 2020 | Tuesday | 936 | 1,581.5 | 358.1 |
| 2020 | Wednesday | 959 | 1,362.6 | 571.1 |

## Gradient boosting on holidays

Holiday flags use the Germany public-holiday calendar and local dates. National holidays are a coarse proxy; regional holidays and special bridge days are not encoded.

| year | holiday | hours | mae_mw | bias_mw |
|---|---|---|---|---|
| 2017 | holiday | 240 | 1,928.6 | -795.5 |
| 2017 | non_holiday | 8,520 | 1,407.8 | -239.0 |
| 2018 | holiday | 216 | 1,705.0 | -554.3 |
| 2018 | non_holiday | 8,520 | 1,577.0 | -218.2 |
| 2019 | holiday | 216 | 1,761.4 | 991.8 |
| 2019 | non_holiday | 8,544 | 1,395.3 | 124.7 |
| 2020 | holiday | 143 | 1,785.7 | 1,348.2 |
| 2020 | non_holiday | 6,433 | 1,407.0 | 296.6 |

## Annual load distribution

| year | hours | mean_mw | median_mw | std_mw | p05_mw | p95_mw |
|---|---|---|---|---|---|---|
| 2015 | 8,759 | 54,738.5 | 54,385.0 | 9,889.7 | 39,251.0 | 69,448.4 |
| 2016 | 8,784 | 55,440.9 | 54,974.0 | 10,071.8 | 39,784.8 | 70,573.1 |
| 2017 | 8,760 | 56,178.0 | 55,883.5 | 10,165.0 | 40,385.4 | 71,922.6 |
| 2018 | 8,760 | 56,951.3 | 56,568.0 | 9,869.8 | 41,542.7 | 71,705.1 |
| 2019 | 8,760 | 55,990.3 | 55,497.5 | 9,892.5 | 40,489.6 | 71,134.6 |
| 2020 | 6,577 | 53,046.2 | 52,828.0 | 9,734.6 | 37,916.6 | 69,851.4 |

## Lowest and highest monthly average load

| local_month | hours | mean_mw | median_mw | std_mw | change_from_previous_month_mw |
|---|---|---|---|---|---|
| 2015-05 | 744 | 50,703.1 | 48,467.5 | 9,690.2 | -2,014.2 |
| 2017-01 | 744 | 61,312.4 | 61,340.0 | 9,766.7 | 3,832.4 |
| 2017-02 | 672 | 60,657.2 | 60,640.0 | 9,401.0 | -655.2 |
| 2018-02 | 672 | 61,158.2 | 61,125.5 | 8,777.0 | 1,449.4 |
| 2019-01 | 744 | 61,579.0 | 61,739.0 | 9,755.6 | 3,693.7 |
| 2019-02 | 672 | 60,611.5 | 61,098.5 | 9,037.5 | -967.5 |
| 2020-04 | 720 | 49,441.0 | 48,869.5 | 7,921.9 | -6,777.4 |
| 2020-05 | 744 | 48,682.2 | 47,236.0 | 8,449.4 | -758.8 |
| 2020-06 | 720 | 49,621.1 | 49,117.5 | 8,898.9 | 938.9 |
| 2020-08 | 744 | 50,800.4 | 49,480.0 | 8,879.5 | -331.8 |

## What the evidence says

- The published forecast's bias changes substantially between folds; gradient boosting's bias is smaller and changes sign between folds. This is a measured pattern, not an explanation for why it occurred.
- Gradient boosting error varies by season and local hour. In these folds, daytime/late-afternoon hours are often harder than overnight hours; inspect the hour table for year-specific differences rather than treating that as universal.
- Public-holiday hours have higher gradient-boosting MAE than non-holiday hours in every scored year, based on only 143–240 holiday hours per period. Holiday bias also changes direction between years, so the pattern warrants checking holiday definitions and special days before any feature change.
- Monthly average load has visible variation, including the 2020 spring reference period. This flags a possible regime or composition change for follow-up; it does not establish a structural break or its cause.
- The current predictions contain no archived weather forecasts, source-vintage history, or operating covariates. Weather, pandemic-related behavior, holidays, reporting changes, and methodology changes remain hypotheses until matched to evidence.
- Residual autocorrelation and formal change-point testing are not established in this pass. They need explicit analysis before making those claims. The final 2020 local October fragment (two hours) is excluded from monthly extrema summaries.

## Artifacts

- `data/processed/fold_error_slices.csv`
- `data/processed/annual_load_distribution.csv`
- `data/processed/monthly_load_distribution.csv`
