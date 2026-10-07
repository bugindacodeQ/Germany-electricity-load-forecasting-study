# Decision charter: Germany day-ahead load forecast

## Purpose

This is a portfolio case study using public, national-level data. It tests whether a forecast method can improve the hourly day-ahead estimate available to a hypothetical power-system planning analyst. It does not claim to control dispatch, improve a specific firm's operations, or generate savings.

## User and action

- **Intended user:** a hypothetical day-ahead power-system planner responsible for reviewing expected hourly system load.
- **Decision supported:** whether to use the candidate forecast as an additional planning estimate for the next day's hourly load schedule, subject to analyst review.
- **Forecast target:** Germany's national actual total load, in MW, for each hour of the next UTC day.
- **Forecast horizon:** 24 hourly values.
- **Assumed issue cutoff:** 12:00 UTC on the preceding day, solely as a reproducible study convention. It is not asserted to be the cutoff used by a specific TSO or market participant.

## Success measures

- **Primary:** mean absolute error (MAE) in MW over all forecast hours, comparing all methods on the same timestamps.
- **Secondary:** RMSE, signed bias, peak-demand MAE, and performance by season and local hour.
- A candidate is considered promising only if its advantage is repeated across pre-2020 rolling validation periods. A difference in MAE alone does not establish operational or financial value.

## Error costs and limits

The public dataset contains no procurement, reserve, balancing, dispatch, or outage cost data. It therefore cannot establish whether underforecasting or overforecasting costs more, nor translate a MW error into money. The analysis will report both error direction and magnitude without inventing a cost function.

National German load is not an individual utility, industrial plant, or mini-grid load profile. Findings can motivate a stakeholder discovery conversation, but any operational recommendation would require the relevant operator's data, forecast cutoff, action rules, and asymmetric error costs.

## Decision statement

> Given only information available by the stated cutoff, can a reproducible model improve the accuracy of Germany's next-day hourly national-load estimate enough to merit analyst review, compared with simple historical baselines and the published ENTSO-E forecast values preserved in the OPSD export?

The published forecast comparison is provisional because the OPSD export does not include each value's issue or revision timestamp. Treat it as a historical reference series until forecast vintages can be verified.
