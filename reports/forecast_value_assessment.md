# Forecast-value assessment: what current evidence supports

## Current decision context

The project charter names a **hypothetical** day-ahead system planner and a possible action: review the next-day national load estimate as planning input. There is no participating firm or operator, confirmed operational decision, current process forecast vintage, procurement/dispatch record, or cost data. The public national-load forecast is also not a plant, utility-customer, or mini-grid load forecast.

So this assessment does **not** claim savings or assign a euro value to MW error. It defines the evidence and cost inputs required to test value with an actual operator.

## Directional error exposure in the historical development folds

Forecast error is prediction minus actual. Negative error means underforecast; positive error means overforecast. The MWh-equivalent figures below sum each hourly MW error over its one-hour interval and average by UTC day. They describe the size and direction of forecast discrepancies; they are **not** energy left unserved, excess power purchased, imbalance settlement, or realized operating cost.

| model | hours | utc_days | mae_mw | bias_mw | underforecast_hours_pct | overforecast_hours_pct | mean_underforecast_mwh_equiv_per_day | mean_overforecast_mwh_equiv_per_day |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gradient_boosting | 26,256 | 1,095 | 1,468.7 | -111.4 | 53.3 | 46.7 | 18,944.7 | 16,272.9 |
| neural_network | 26,256 | 1,095 | 1,511.4 | -312.6 | 59.7 | 40.3 | 21,868.4 | 14,371.6 |
| published_reference | 26,256 | 1,095 | 1,654.1 | -752.6 | 65.4 | 34.6 | 28,854.1 | 10,808.3 |
| same_hour_168h | 26,256 | 1,095 | 2,520.2 | 17.7 | 50.9 | 49.1 | 30,002.8 | 30,427.8 |

The detailed year-specific table is in `data/processed/directional_error_summary.csv`. These are the already-inspected 2017–2019 development periods. OPSD forecast vintages are unverified, so the published-reference row is only a comparison against values in the export.

## Value calculation once a real decision is available

For hourly interval t of duration h_t, a simple screening calculation can translate errors into quantities:

- underforecast MWh: `max(actual_MW - forecast_MW, 0) × h_t`
- overforecast MWh: `max(forecast_MW - actual_MW, 0) × h_t`
- screening cost: `underforecast_MWh × shortfall_cost_t + overforecast_MWh × surplus_cost_t`

The two cost rates must come from the operator's actual decision and tariff/settlement/dispatch process. This linear form is only a first-pass approximation; many operating costs are nonlinear, constrained, and dependent on the action taken. The preferred evaluation replays the real decision or settlement process using incumbent and candidate forecasts under identical conditions.

Then compare `incumbent total cost − candidate total cost − incremental model/implementation cost` on a later untouched period. Define the success threshold with the stakeholder before the evaluation. Include risk measures for high-cost hours and under/overforecast separately, not just average MAE.

## Minimum stakeholder and data inputs

| Input | Why it is needed |
|---|---|
| Named user and specific action changed by the forecast | Shows how an accuracy change can affect operations |
| Actual target geography and delivery-time convention | Aligns national/UTC targets with the user's meter, zone, and local operating day |
| Forecast issue cutoff and archived forecast vintages | Ensures each compared forecast was available when the decision was made |
| Incumbent forecast and current action/plan | Establishes the true business baseline |
| Underforecast and overforecast consequence by interval | Captures asymmetric costs and reliability/service penalties |
| Procurement, balancing, reserve, dispatch, or process replay data | Converts forecast errors into decision-level outcomes |
| Model run, integration, monitoring, and analyst costs | Accounts for the cost of deploying the candidate |
| Stakeholder-defined materiality and risk limits | Sets the acceptance threshold before results are seen |

## Pilot design

1. Agree on the target, cutoff, action, baseline, cost calculation, and acceptance threshold before collecting pilot outcomes.
2. Archive candidate and incumbent forecasts with issue time, revision, model version, and the information available at issue time.
3. Run in shadow mode for at least one full seasonal cycle where practical; do not change live operations based on this public-data study.
4. Replay the actual decision or cost process on identical intervals. Report paired net value, under/over costs, high-cost-event behavior, and uncertainty using time-block resampling.
5. Make a deployment decision only if the stakeholder-defined net-value and risk criteria are met on data not used for model selection.

## Assessment status

**Value framework complete; financial-value gate remains open.** Current public data supports describing forecast accuracy and directional error exposure only. A real user, action, forecast-vintage archive, and cost model are required before estimating business value.

## Artifacts

- `data/processed/directional_error_summary.csv`
- `scripts/assess_forecast_value.py`
