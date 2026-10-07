import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import compare_models_folds


class ModelComparisonTests(unittest.TestCase):
    def test_main_writes_fold_artifacts_and_report(self):
        index = pd.DatetimeIndex([
            "2016-12-31 00:00:00+00:00",
            "2017-01-01 00:00:00+00:00",
            "2017-12-31 00:00:00+00:00",
            "2018-01-01 00:00:00+00:00",
            "2018-12-31 00:00:00+00:00",
            "2019-01-01 00:00:00+00:00",
            "2019-12-31 00:00:00+00:00",
        ])
        data = pd.DataFrame({
            "actual_mw": np.arange(7, dtype=float) + 100,
            "published_day_ahead": np.arange(7, dtype=float) + 101,
            "lag_48h": np.arange(7, dtype=float) + 99,
            "lag_168h": np.arange(7, dtype=float) + 98,
            "lag_336h": np.arange(7, dtype=float) + 97,
        }, index=index)
        for feature in compare_models_folds.FEATURES:
            if feature not in data:
                data[feature] = 0.0

        def fake_predictions(train, validation):
            return {name: validation.actual_mw.to_numpy() + offset
                    for name, offset in zip(compare_models_folds.MODELS, range(1, 8))}

        def fake_bootstrap(predictions, candidate, reference, draws=10_000, seed=42):
            return {
                "candidate": candidate,
                "reference": reference,
                "mae_gain_mw_candidate_better_positive": 1.0,
                "ci95_low_mw": 0.0,
                "ci95_high_mw": 2.0,
                "bootstrap_days": 3,
                "draws": draws,
            }

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with (
                patch.object(compare_models_folds, "load_features", return_value=data),
                patch.object(compare_models_folds, "fit_predict", side_effect=fake_predictions),
                patch.object(compare_models_folds, "paired_day_bootstrap", side_effect=fake_bootstrap),
                patch.object(compare_models_folds, "OUT", output),
                patch.object(compare_models_folds, "REPORT", output / "comparison.md"),
            ):
                compare_models_folds.main()

            self.assertTrue((output / "expanding_fold_predictions.csv").is_file())
            self.assertTrue((output / "expanding_fold_metrics.csv").is_file())
            self.assertTrue((output / "paired_model_comparisons.csv").is_file())
            report = (output / "comparison.md").read_text(encoding="utf-8")
            self.assertIn("Gradient boosting MAEs were", report)
            self.assertIn("2017", report)
            self.assertIn("2019", report)


if __name__ == "__main__":
    unittest.main()
