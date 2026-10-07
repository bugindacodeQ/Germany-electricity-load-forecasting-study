# Expanding-window model comparison

## Design

All models are evaluated on the same nonmissing timestamps in 2017, 2018, and 2019. Each learned model is fitted once at the start of each year using only prior data, then held fixed for that year. Lag and calendar features update by target timestamp. Specifications are fixed: Ridge alpha=10; histogram gradient boosting (250 iterations, learning rate 0.05, 31 leaves, depth 6, L2=1); the two-hidden-layer PyTorch network (64/32 units, 35 epochs, seed 42); and Prophet with daily/weekly/yearly seasonality plus a 168-hour load regressor. Scaling is fitted on training data only. No hyperparameter search was performed in this benchmark.

The holiday-aware policy is omitted from fold selection because its rule was selected using 2019, so scoring it on 2019 would reuse its selection data. The OPSD published forecast is retained as an external historical reference; its issue/revision vintage is unknown. These folds have already been inspected in earlier work, so all results below remain exploratory development evidence. Prophet emitted a warning that the first fold has fewer than two years of training history for yearly seasonality; interpret that fold's Prophet result cautiously.

## Fold results

| year | model | hours | mae_mw | rmse_mw | bias_mw | high_load_mae_mw |
| --- | --- | --- | --- | --- | --- | --- |
| 2017 | published_reference | 8,760 | 1,395.8 | 1,802.3 | -449.0 | 1,769.5 |
| 2017 | gradient_boosting | 8,760 | 1,422.0 | 1,974.6 | -254.2 | 1,751.3 |
| 2017 | neural_network | 8,760 | 1,472.8 | 2,087.1 | -553.3 | 2,035.5 |
| 2017 | ridge | 8,760 | 1,966.3 | 2,853.1 | -153.3 | 2,407.5 |
| 2017 | same_hour_168h | 8,760 | 2,445.8 | 4,415.5 | 14.1 | 2,609.0 |
| 2017 | prophet | 8,760 | 4,861.1 | 5,606.1 | -4,296.9 | 5,587.8 |
| 2017 | same_hour_48h | 8,760 | 7,338.5 | 9,825.2 | 17.1 | 7,295.0 |
| 2018 | published_reference | 8,736 | 1,577.1 | 1,999.0 | -474.6 | 2,106.4 |
| 2018 | gradient_boosting | 8,736 | 1,580.1 | 2,133.4 | -226.5 | 1,956.3 |
| 2018 | neural_network | 8,736 | 1,602.1 | 2,332.8 | -583.0 | 1,881.8 |
| 2018 | ridge | 8,736 | 2,082.5 | 2,973.5 | -181.9 | 2,395.0 |
| 2018 | same_hour_168h | 8,736 | 2,556.9 | 4,368.6 | -12.6 | 2,638.0 |
| 2018 | prophet | 8,736 | 2,669.7 | 3,721.7 | -1,189.6 | 3,109.4 |
| 2018 | same_hour_48h | 8,736 | 7,360.4 | 9,794.5 | 16.0 | 7,153.9 |
| 2019 | gradient_boosting | 8,760 | 1,404.4 | 1,913.6 | 146.1 | 1,388.4 |
| 2019 | neural_network | 8,760 | 1,459.5 | 2,229.0 | 197.5 | 1,420.0 |
| 2019 | published_reference | 8,760 | 1,989.2 | 2,489.4 | -1,333.5 | 2,894.9 |
| 2019 | ridge | 8,760 | 2,080.1 | 3,014.5 | 21.6 | 2,493.7 |
| 2019 | prophet | 8,760 | 2,395.1 | 3,588.2 | -194.7 | 2,556.4 |
| 2019 | same_hour_168h | 8,760 | 2,558.1 | 4,465.0 | 51.5 | 2,745.2 |
| 2019 | same_hour_48h | 8,760 | 7,376.7 | 9,741.8 | -5.2 | 7,170.7 |

## Pooled out-of-fold results

| model | hours | mae_mw | rmse_mw | bias_mw | high_load_mae_mw |
| --- | --- | --- | --- | --- | --- |
| gradient_boosting | 26,256 | 1,468.7 | 2,009.2 | -111.4 | 1,730.3 |
| neural_network | 26,256 | 1,511.4 | 2,218.5 | -312.7 | 1,812.7 |
| published_reference | 26,256 | 1,654.1 | 2,116.8 | -752.6 | 2,197.8 |
| ridge | 26,256 | 2,042.9 | 2,947.8 | -104.5 | 2,426.0 |
| same_hour_168h | 26,256 | 2,520.2 | 4,416.6 | 17.7 | 2,656.4 |
| prophet | 26,256 | 3,309.2 | 4,403.4 | -1,894.4 | 3,847.6 |
| same_hour_48h | 26,256 | 7,358.5 | 9,787.2 | 9.3 | 7,208.9 |

High load is defined within each fold using that fold's training-set 90th percentile. Bias is prediction minus actual; positive is overforecast.

## Paired day-level uncertainty

| candidate | reference | mae_gain_mw_candidate_better_positive | ci95_low_mw | ci95_high_mw | bootstrap_days |
| --- | --- | --- | --- | --- | --- |
| same_hour_48h | same_hour_168h | -4,838.3 | -5,211.8 | -4,474.3 | 1,095 |
| ridge | same_hour_168h | 477.3 | 352.7 | 607.0 | 1,095 |
| gradient_boosting | same_hour_168h | 1,051.5 | 883.5 | 1,226.1 | 1,095 |
| neural_network | same_hour_168h | 1,008.9 | 841.8 | 1,180.5 | 1,095 |
| prophet | same_hour_168h | -789.0 | -912.0 | -660.6 | 1,095 |
| same_hour_48h | published_reference | -5,704.4 | -6,013.9 | -5,391.8 | 1,095 |
| ridge | published_reference | -388.8 | -488.0 | -293.6 | 1,095 |
| gradient_boosting | published_reference | 185.4 | 116.0 | 253.6 | 1,095 |
| neural_network | published_reference | 142.7 | 60.3 | 222.3 | 1,095 |
| prophet | published_reference | -1,655.1 | -1,782.6 | -1,527.5 | 1,095 |
| neural_network | gradient_boosting | -42.6 | -103.8 | 17.2 | 1,095 |
| ridge | gradient_boosting | -574.2 | -651.4 | -498.8 | 1,095 |
| prophet | gradient_boosting | -1,840.5 | -1,959.4 | -1,722.6 | 1,095 |
| published_reference | gradient_boosting | -185.4 | -252.6 | -114.7 | 1,095 |
| same_hour_168h | gradient_boosting | -1,051.5 | -1,224.5 | -881.1 | 1,095 |

Positive paired gain means the candidate's absolute error is lower. Comparisons include each candidate against the weekly naive and published reference, plus candidate checks against gradient boosting. The 95% intervals resample whole UTC days independently within each fold (10,000 draws), preserving within-day dependence. They do not account for all between-day serial dependence, and should be treated as approximate.

## Decision readout

- Gradient boosting had the lowest pooled hourly MAE at 1,468.7 MW. It beat the weekly-naive baseline by 1,051.5 MW; the paired day-bootstrap 95% interval was [883.5, 1,226.1] MW.
- Neural network was the closest learned model (annual MAEs 1,472.8, 1,602.1, 1,459.5 MW). Its pooled advantage over gradient boosting was -42.6 MW, with 95% interval [-103.8, 17.2] MW; the interval includes zero, so these folds do not establish a clear difference between the two.
- Gradient boosting MAEs were 1,422.0, 1,580.1, and 1,404.4 MW. The published reference was slightly better in 2017 and 2018 (1,395.8 and 1,577.1 MW) but much worse in 2019 (1,989.2 MW). Its issue/revision vintage is unverified, so the pooled gain of 185.4 MW is only a historical export comparison.
- Ridge and the current Prophet specification underperformed gradient boosting on these folds. Prophet's first fold also triggered a short-history warning for yearly seasonality; this diagnoses this specification, not Prophet as a whole.
- Treat these model rankings as exploratory because all three folds have already been inspected. They guide what to test later; they do not provide independent confirmation.
- The 2020 period was not used here and remains a previously viewed historical reference, not a fresh test.
- Do not claim financial value from MW errors. A later unseen holdout, confirmed target/cutoff, and a stakeholder cost model are still required.

## Artifacts

- `data/processed/expanding_fold_predictions.csv`
- `data/processed/expanding_fold_metrics.csv`
- `data/processed/paired_model_comparisons.csv`
