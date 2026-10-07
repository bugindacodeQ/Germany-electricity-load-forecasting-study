# Build the Germany load report in Power BI Desktop

This guide builds an interactive report from the project export. It focuses on German load forecasting; a world choropleth is not appropriate because this dataset contains only one country. Use a separate, harmonized multi-country dataset for a global map question.

## 1. Generate the Power BI file

From PowerShell in the project root, after the source data and benchmark outputs exist:

```powershell
python scripts/compare_models_folds.py
python scripts/export_powerbi.py
```

The exporter writes `data/processed/germany_powerbi_hourly.csv`. It contains one row per UTC hour, actual load, the OPSD published forecast reference, model predictions for the common 2017–2019 folds, German local calendar fields, and optional generation/price context. Rows outside those folds have blank candidate-model predictions. The published forecast vintage is unverified.

The gradient-boosting column is **not** blank throughout: the checked export has 26,256 nonblank hourly predictions, all in the 2017–2019 backtest folds. It is blank outside those folds by design. In Power BI, make sure this field is summarized as **Average** (or use a measure) rather than **Count**. A count plots the number of prediction rows, not forecast MW. The hourly timestamp should be used as the plain `utc_timestamp` field, not its automatic date hierarchy, when building an hourly chart.

## 2. Import and type the fields

1. Open Power BI Desktop and create a blank report.
2. Select **Home → Get data → Text/CSV**, choose `data/processed/germany_powerbi_hourly.csv`, then select **Transform Data**. The Text/CSV connector opens Power Query for preview and type checks ([Microsoft guide](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)).
3. In Power Query, set `utc_timestamp` to **Date/Time**. Its values are UTC even though Power BI's Date/Time type has no time-zone field. Keep the column name, chart title, and page labels explicit about UTC.
4. Set `date_utc` and `date_berlin` to **Date**; `year`, month, hour, and weekday numbers to **Whole Number**; load, forecast, error, generation, and price values to **Decimal Number**.
5. Rename the query to `LoadHourly`, then select **Close & Apply**.
6. In Data view, confirm the first and last dates, hourly row count (about 50,401), and a few load values. The exporter and raw source should agree.
7. Select `LoadHourly[month_name]` and choose **Column tools → Sort by column → month_number**. Sort `weekday_name_berlin` by `weekday_number_berlin` as well.

If Power Query assigns the timestamp as text, select the column and use **Data type → Date/Time**. The exported values are formatted `YYYY-MM-DD HH:MM:SS`; interpret them as UTC. Do not apply a local computer time-zone conversion to the UTC field.

For consistent date filtering, create a calendar table from **Modeling → New table**:

```DAX
DateCalendar =
ADDCOLUMNS (
    CALENDAR ( MIN ( LoadHourly[date_utc] ), MAX ( LoadHourly[date_utc] ) ),
    "Year", YEAR ( [Date] ),
    "Month Number", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "MMMM" ),
    "Weekday Number", WEEKDAY ( [Date], 2 ),
    "Weekday", FORMAT ( [Date], "dddd" )
)
```

In Model view, create a one-to-many, single-direction relationship from `DateCalendar[Date]` to `LoadHourly[date_utc]`. Sort `DateCalendar[Month]` by `DateCalendar[Month Number]` and `DateCalendar[Weekday]` by `DateCalendar[Weekday Number]`. Use the calendar table for UTC date, year, and month slicers. Use `LoadHourly[date_berlin]` when filtering by the German local date. A dedicated date table gives explicit control over date filtering and hierarchies ([Microsoft date-table guide](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables)).

## 3. Add measures

In the Fields pane, right-click `LoadHourly` and select **New measure**. Add these measures one by one. Measures recalculate with report filters and slicers ([Microsoft overview](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-calculations-options)).

```DAX
Average Actual Load (MW) =
AVERAGE ( LoadHourly[actual_load_mw] )

Published Forecast MAE (MW) =
AVERAGEX (
    FILTER (
        LoadHourly,
        NOT ISBLANK ( LoadHourly[actual_load_mw] )
            && NOT ISBLANK ( LoadHourly[published_forecast_mw] )
            && NOT ISBLANK ( LoadHourly[gradient_boosting_forecast_mw] )
    ),
    ABS ( LoadHourly[published_forecast_mw] - LoadHourly[actual_load_mw] )
)

Gradient Boosting MAE (MW) =
AVERAGEX (
    FILTER (
        LoadHourly,
        NOT ISBLANK ( LoadHourly[actual_load_mw] )
            && NOT ISBLANK ( LoadHourly[gradient_boosting_forecast_mw] )
    ),
    ABS ( LoadHourly[gradient_boosting_forecast_mw] - LoadHourly[actual_load_mw] )
)

Neural Network MAE (MW) =
AVERAGEX (
    FILTER (
        LoadHourly,
        NOT ISBLANK ( LoadHourly[actual_load_mw] )
            && NOT ISBLANK ( LoadHourly[neural_network_forecast_mw] )
    ),
    ABS ( LoadHourly[neural_network_forecast_mw] - LoadHourly[actual_load_mw] )
)

Published Forecast Bias (MW) =
AVERAGEX (
    FILTER (
        LoadHourly,
        NOT ISBLANK ( LoadHourly[actual_load_mw] )
            && NOT ISBLANK ( LoadHourly[published_forecast_mw] )
            && NOT ISBLANK ( LoadHourly[gradient_boosting_forecast_mw] )
    ),
    LoadHourly[published_forecast_mw] - LoadHourly[actual_load_mw]
)

Gradient Boosting Bias (MW) =
AVERAGEX (
    FILTER (
        LoadHourly,
        NOT ISBLANK ( LoadHourly[actual_load_mw] )
            && NOT ISBLANK ( LoadHourly[gradient_boosting_forecast_mw] )
    ),
    LoadHourly[gradient_boosting_forecast_mw] - LoadHourly[actual_load_mw]
)

Backtest Hours =
CALCULATE (
    COUNTROWS ( LoadHourly ),
    NOT ISBLANK ( LoadHourly[gradient_boosting_forecast_mw] )
)
```

These comparison measures use only rows where the candidate predictions exist; the export contains predictions for 2017–2019 only. The published forecast has missing values in the source, so its measure uses complete common rows. Error is forecast minus actual: a positive bias is overforecasting. Do not sum MW errors as if they were energy or money.

## 4. Create the report pages

Use a 16:9 canvas. Keep titles and units visible, use a restrained palette (actual load: deep navy; candidate forecast: teal; published reference: amber; error: red/blue), and avoid 3D effects. A clean layout could use a white or very light gray background with dark text.

### Page 1 — System overview

- Add a title: **Germany electricity load | hourly forecast review**.
- Add four cards: Average Actual Load (MW), Gradient Boosting MAE (MW), Published Forecast MAE (MW), and Backtest Hours.
- Add a line chart with `utc_timestamp` on the X-axis and `actual_load_mw`, `gradient_boosting_forecast_mw`, and `published_forecast_mw` as values. Set the X-axis to **Continuous** and turn off the automatic date hierarchy. Use a date slicer to zoom to a week or month.
- Add slicers for `DateCalendar[Year]`, `DateCalendar[Date]`, and (if needed) `LoadHourly[date_berlin]`. Label the date slicers clearly so users know which convention they use.
- Add a small text box: “Model forecasts shown for development folds 2017–2019. Results are exploratory; published-forecast issue/revision times are unavailable.”

For long periods, use daily averages or a date slicer to avoid drawing every hour across six years. Keep the detailed hourly line view for short selections. Power BI line charts support continuous axes and multiple series ([formatting reference](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-line-chart)).

### Page 2 — Forecast performance

- Add cards for Gradient Boosting MAE, Neural Network MAE, Published Forecast MAE, and Gradient Boosting Bias.
- Add a clustered column chart with `year` on the X-axis and suitable MAE measures as values. Use only 2017–2019. The OPSD value is a historical export reference, not a verified real-time comparator.
- Add a line chart with `hour_berlin` on the X-axis and a model MAE measure as the value. Add `year` as the legend or slicer. Explain that the repeated local hour in autumn is aggregated into the same local-hour bin.
- Add a table with year, MAE measures, bias measures, and `Backtest Hours`; apply conditional formatting to MAE and bias for quick scanning.

### Page 3 — Load patterns and context

- Add a matrix with `weekday_name_berlin` as rows, `hour_berlin` as columns, and Average Actual Load (MW) as values. Apply a light-to-dark conditional background scale.
- Add a monthly line chart of average actual load using `month_name` sorted by `month_number`.
- Optionally add solar and wind generation trends. Treat them as descriptive context only: realized generation was not available at the day-ahead forecast cutoff and was not used as a model feature.
- If you include the day-ahead price field, filter blanks and label it “Germany–Luxembourg bidding zone”; it is not a Germany-only price series.

## 5. Format and connect interactions

1. Use concise visual titles with units, for example “Hourly load (MW, UTC)” and “Mean absolute error (MW)”.
2. Set card and axis display units to none or thousands consistently; avoid mixing scales on one axis.
3. Keep gridlines subtle, legends near the chart, and labels readable at report-page size. Turn markers off for dense hourly lines; use them only for monthly or daily summaries.
4. Select **Format → Edit interactions** and confirm that date/year slicers filter every relevant visual. Test each visual selection and disable interactions that create confusing cross-highlighting ([Microsoft guide](https://learn.microsoft.com/en-us/power-bi/create-reports/service-reports-visual-interactions)).
5. Use tooltips to show timestamp, actual MW, forecast MW, signed error, and absolute error. The sign convention should appear in a tooltip note or page subtitle.
6. Add a small “About this analysis” page with data source/version, UTC horizon, assumed cutoff, development-only status, known missing values, and unverified forecast vintage.

## 6. Final checks and save

- Confirm the table contains about 50,401 rows and timestamps are treated as UTC.
- Confirm forecast MAE cards evaluate only common 2017–2019 prediction rows; they should not silently compare one model over a different date range.
- Filter a short week and verify the line chart shows actual and forecast values at the same hours.
- Check daylight-saving dates, missing forecast intervals, slicer interactions, and every displayed unit.
- Save the report as `reports/germany_load_forecasting.pbix` if you want the Power BI report itself included in the portfolio. The `.pbix` is not generated by the Python scripts.
- For GitHub, also export page screenshots to `reports/figures/` if you want a visual preview in the README. Do not commit the 130 MB source CSV or derived hourly export.

## References

- [Import text and CSV files with Power Query](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)
- [Power BI line charts and axis options](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-line-chart)
- [Measures and other calculation options](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-calculations-options)
- [Change how visuals interact](https://learn.microsoft.com/en-us/power-bi/create-reports/service-reports-visual-interactions)
