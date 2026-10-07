# Evaluation protocol

This protocol fixes the study assumptions and rules before the next model comparison. It does not make existing scores out-of-sample: results from 2017–2020 have already been inspected during exploration and model comparison.

## Forecast task

- **Target:** hourly German actual total load, MW.
- **Target time convention:** UTC hour-start timestamps, forecasting the next UTC calendar day (24 values).
- **Issue cutoff:** 12:00 UTC on D-1 as a project convention, not a verified German operator cutoff.
- **Potential inputs:** calendar variables, load values from 48, 168, and 336 elapsed hours before each target time, and German local-date holiday flags. Check feature availability for every candidate.
- **Excluded inputs:** target-day actual values, realized weather, actual same-day renewable output, or market prices unavailable at the cutoff.
- **Missing data:** do not impute target or benchmark values for the primary score. Score only common observed target timestamps and report exclusions by fold.

## Development backtest

Use expanding-window annual origins:

| Fold | Training data | Validation period |
|---|---|---|
| 1 | All eligible data before 2017-01-01 | 2017 |
| 2 | All eligible data before 2018-01-01 | 2018 |
| 3 | All eligible data before 2019-01-01 | 2019 |

Fit preprocessing and learned transformations on each fold's training data only. Freeze model settings before scoring folds. These years have already been examined, so reruns are **development diagnostics**, not independent final confirmation. The 2020 results are also already viewed and are historical reference only; do not select features or models based on 2020.

For the next model comparison, refit each learned model at the start of each validation year and keep its fitted parameters fixed for that year. At each forecast origin, update only features observable by the stated cutoff (such as lagged actual load). Keep simple lag baselines available at all forecast origins.

## Comparators

1. Same hour one week earlier (168-hour seasonal naive).
2. Same hour 48 hours earlier (secondary simple baseline).
3. The locked holiday-aware rule from the 2019 development experiment, reported as a candidate heuristic.
4. The ENTSO-E published day-ahead series in OPSD, reported as a historical reference only until its issue/revision vintage is established.
5. Candidate learned models with fixed specifications.

## Metrics and aggregation

- **Primary:** MAE in MW over all common scored hourly points.
- **Secondary:** RMSE, signed bias (forecast minus actual), and high-load MAE.
- Define high load for each fold using the 90th percentile of that fold's training actual load; do not compute the threshold from validation targets.
- Report pooled out-of-fold metrics and each annual fold separately. Report sample counts and missing-hour exclusions.
- For paired model comparisons, report fold-level differences and an uncertainty interval resampling whole days, preserving within-day dependence.
- Do not convert error metrics into financial value without a stakeholder cost model.

## Model selection and final evaluation

Use the three historical annual folds only for development model selection, and document each model or feature change. Since they have already been examined, label results exploratory. The existing 2020 period is not a fresh test. Before making a final generalization claim, acquire a later chronological holdout not used in the current work, verify feature availability and forecast vintages, and lock the model before scoring it.

## Known protocol limitations

- The UTC-day horizon differs from Germany's local delivery day around daylight-saving transitions. Keep UTC for this reproducible study, but revisit the target convention before describing the work as operationally aligned.
- The published forecast's issue and revision timestamps are absent from the OPSD export. Its score is not a verified comparator at the assumed cutoff.
- The national target is not a company or site load profile.
