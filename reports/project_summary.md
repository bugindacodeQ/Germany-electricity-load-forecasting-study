# Germany day-ahead load forecasting — project readout

## Business question

Can a data-driven model improve an hourly next-day estimate of Germany's national electricity load enough to help a day-ahead planner? The current study tests forecast accuracy on public OPSD data. It does not yet test a real company's process or business value.

## Study design

- Target: hourly German actual total load, MW; 24-hour UTC-day horizon.
- Assumed issue time: 12:00 UTC on the preceding day. This is a study convention, not an operator-confirmed cutoff.
- Models: weekly and 48-hour load lags, Ridge, histogram gradient boosting, a small PyTorch neural network, Prophet, and the OPSD published forecast as a historical reference.
- Validation: expanding annual origins for 2017, 2018, and 2019; all methods scored on common timestamps. Gradient boosting, Ridge, neural network, and Prophet were refit at each annual origin.
- Primary metric: MAE; secondary metrics include RMSE, bias, and training-threshold high-load MAE.

## Findings

Gradient boosting had pooled MAE of **1,468.7 MW**, the lowest among the tested candidates. The neural network scored **1,511.4 MW**. Their 42.6 MW difference is small, and the paired day-bootstrap interval includes zero. Gradient boosting's MAEs were 1,422.0 MW in 2017, 1,580.1 MW in 2018, and 1,404.4 MW in 2019. The OPSD published values scored better in 2017 and 2018, then worse in 2019.

Errors vary by season, local hour, weekday, holidays, and demand range. Directional summaries report under- and overforecast error separately. Their MWh-equivalent figures are forecast-error volume over hourly intervals—not energy unserved, imbalance cost, or realized savings.

## What is established

- The analysis code, notebook, evaluation protocol, feature-timing check, diagnostics, and Power BI export path are documented.
- Lag timestamps and calendar features precede the assumed forecast cutoff. Actual source-value publication/revision timing has not been verified.
- OPSD published forecast vintages are unknown, so its comparison is not a confirmed real-time benchmark.

## What is not established

- All 2017–2019 folds and the 2020 historical reference have already been inspected. There is no untouched test set and no final generalization claim.
- No real operator, company load profile, or confirmed operational decision is represented.
- No procurement, reserve, dispatch, settlement, or outage cost model is available. Financial value cannot be calculated.

## Recommended next evidence

Identify an operator and decision owner; confirm geography, local/UTC horizon, and forecast cutoff; obtain incumbent forecast vintages and operational records; agree on asymmetric costs and acceptance criteria; then run a shadow pilot and cost replay on a later untouched period.

**Conclusion:** the project demonstrates applied forecasting and careful validation, but it is a research/portfolio prototype rather than an operational product or savings case.
