# What forecasting a national power system taught me about applied data science

*An exploratory benchmark of Germany’s hourly electricity load, using Open Power System Data.*

## The question I wanted to answer

I began with a broad interest in using data science to solve energy problems. To make that concrete, I chose a question with a measurable target: can a model forecast Germany’s hourly electricity demand for the next day more accurately than simple historical baselines?

The target was total German load in megawatts. I treated the task as a 24-hour forecast horizon and assumed a 12:00 UTC issue cutoff on the previous day. That cutoff is a study convention; it is not a verified operating schedule for a German grid operator.

I used the Open Power System Data (OPSD) time-series package, which compiles public electricity-system data. This is national-level historical data, not the load profile of a specific utility, factory, or customer.

## Turning a modeling task into a decision question

The first useful step was defining what “better” would mean. I used mean absolute error (MAE), measured in MW, as the primary comparison metric. I also tracked RMSE, signed bias, and errors during high-load periods.

A forecast with lower error could be useful to a planner, but error reduction alone does not establish business value. To claim savings, we would need a real decision process, an incumbent forecast, the cost of over- and under-forecasting, and evidence that decisions would change. This dataset contains none of those things, so this project evaluates accuracy rather than financial impact.

## Models and evaluation

I compared seasonal-naive forecasts with Ridge regression, histogram gradient boosting, a small neural network, and Prophet. I also included the published forecast values in the OPSD export as a historical reference. The model features used calendar information and lagged load values available before the assumed cutoff.

The main benchmark used expanding annual folds for 2017, 2018, and 2019. At each annual origin, models trained on earlier observations and were evaluated on that year. Every candidate was scored on common timestamps. I used a paired day-level bootstrap to estimate uncertainty in differences between model MAEs.

These are development folds, not an untouched final test. The folds had already been examined during the project, and I had also viewed a 2020 reference period. The results should therefore be treated as exploratory evidence, not a final estimate of future performance.

## What I found

Gradient boosting had the lowest pooled MAE among the tested models: **1,468.7 MW** over 26,256 hourly predictions. The neural network scored **1,511.4 MW**. Its estimated 42.6 MW advantage over gradient boosting had a paired day-bootstrap 95% interval from -103.8 to 17.2 MW, which includes zero. These folds do not establish a clear difference between those two models.

The weekly seasonal-naive forecast scored **2,520.2 MW** MAE. On these folds, gradient boosting reduced MAE by about 1,051.5 MW versus that baseline. This is a meaningful benchmark result for this dataset and protocol, but it is not a guaranteed improvement in a live energy operation.

Prophet scored worse than the other leading approaches with the current specification. Its first fold also had less than two years of training history for yearly seasonality. That result says the specification needs work; it does not prove Prophet is unsuitable for energy forecasting generally.

The published forecast reference scored **1,654.1 MW** pooled MAE. It performed slightly better than gradient boosting in 2017 and 2018, then worse in 2019. Crucially, the dataset does not provide the publication or revision timestamps needed to verify whether those values were available at the assumed issue time. I therefore cannot call this a confirmed real-time benchmark.

## A practical snag: the Power BI line looked empty

When I loaded the export into Power BI, the gradient boosting series appeared as zero or blank. Inspecting the CSV showed the predictions were present: 26,256 rows had values, corresponding to the 2017–2019 backtest folds. Other dates were blank by design because the model had not generated predictions for them.

Power BI had treated the forecast column as a **Count**, which counts populated rows rather than summing or averaging forecast MW. It had also used the timestamp’s automatic date hierarchy, grouping the chart at a coarser level than the hourly series. The practical fix is to plot the plain UTC timestamp, use a numeric aggregation or explicit measure, and filter to the backtest period when comparing forecasts.

This was a useful reminder that a correct modeling pipeline can still produce a misleading visualization if field types, aggregation, or time hierarchy are wrong. The project includes a Power BI guide with the field names, DAX measures, and suggested report pages.

## What this project does and does not show

It shows an end-to-end applied workflow: defining a target and horizon, auditing data, checking feature timing, comparing baselines with statistical and machine-learning models, examining errors, and preparing an export for visualization.

It does not show that a grid operator should deploy gradient boosting, that an energy company would save money, or that the model generalizes to another country or customer. The study relies on historical national data, the forecast cutoff is assumed, the published forecast vintage is unknown, and no untouched test period remains.

## What I would do next

The next step is not another model by default. I would speak with a potential decision owner and clarify the operating decision, forecast issue time, local delivery-day convention, error costs, and data latency. Then I would secure archived forecasts and a later untouched evaluation period. Only after agreeing on a decision metric would I test whether lower statistical error changes operational outcomes.

That is the main lesson I’m taking from this work: the algorithm is only one part of an energy data-science project. The problem definition, information available at decision time, comparison baseline, and evidence of value matter just as much.

## Reproducibility and source

The code, notebook, reports, model comparison, tests, and Power BI export instructions are in the project repository: **[insert your GitHub repository link]**. The source data is Open Power System Data (2020), *Time series*, version 2020-10-06, [doi:10.25832/time_series/2020-10-06](https://doi.org/10.25832/time_series/2020-10-06). The source dataset is not included in the repository; its license and attribution terms should be followed when reusing the data.

---

*This article reports a portfolio study, not investment advice, grid-operational guidance, or a validated commercial forecast.*
