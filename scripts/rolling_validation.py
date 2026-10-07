"""Annual expanding-window diagnostics before the previously inspected 2020 reference."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from benchmark_ml import FEATURES, load_features


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed" / "rolling_validation_predictions.csv"
REPORT = ROOT / "reports" / "rolling_validation.md"
YEARS = (2017, 2018, 2019)


def main() -> None:
    data = load_features()
    rows = []
    for year in YEARS:
        train = data.loc[data.index < f"{year}-01-01"]
        validation = data.loc[f"{year}-01-01":f"{year}-12-31"]
        model = HistGradientBoostingRegressor(
            max_iter=250, learning_rate=0.05, max_leaf_nodes=31,
            max_depth=6, l2_regularization=1.0, random_state=42,
        )
        model.fit(train[FEATURES], train.actual_mw)
        rows.append(pd.DataFrame({
            "utc_timestamp": validation.index,
            "actual_mw": validation.actual_mw.to_numpy(),
            "published_day_ahead": validation.published_day_ahead.to_numpy(),
            "same_hour_1_week_ago": validation.lag_168h.to_numpy(),
            "gradient_boosting_mw": model.predict(validation[FEATURES]),
            "validation_year": year,
            "training_hours": len(train),
        }))
        print(f"Completed {year}: train={len(train):,}, validation={len(validation):,}", flush=True)

    output = pd.concat(rows, ignore_index=True)
    output.to_csv(OUTPUT, index=False)
    summary = []
    for year, frame in output.groupby("validation_year"):
        for name in ("same_hour_1_week_ago", "published_day_ahead", "gradient_boosting_mw"):
            error = frame[name] - frame.actual_mw
            summary.append({
                "year": year, "model": name, "hours": len(frame),
                "mae_mw": error.abs().mean(),
                "rmse_mw": np.sqrt(error.pow(2).mean()),
                "bias_mw": error.mean(),
            })
    metrics = pd.DataFrame(summary)
    metrics.to_csv(OUTPUT.with_name("rolling_validation_metrics.csv"), index=False)
    table = ["| Year | Method | Hours | MAE MW | RMSE MW | Bias MW |", "|---:|---|---:|---:|---:|---:|"]
    for row in summary:
        table.append(
            f"| {row['year']} | {row['model']} | {row['hours']:,} | "
            f"{row['mae_mw']:,.1f} | {row['rmse_mw']:,.1f} | {row['bias_mw']:,.1f} |"
        )
    report = """# Expanding-window diagnostics before the previously inspected 2020 reference

Gradient boosting settings and features are held fixed from the prior benchmark. Each year is predicted from a model trained only on earlier years. These are historical development diagnostics; the 2020 period has since been inspected and is not an untouched final test. Published forecast timing remains unverified.

""" + "\n".join(table) + "\n"
    REPORT.write_text(report, encoding="utf-8")
    print(metrics.round(1).to_string(index=False))
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
