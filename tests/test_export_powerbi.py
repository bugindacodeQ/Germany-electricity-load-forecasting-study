import tempfile
import unittest
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import export_powerbi


class PowerBIExportTests(unittest.TestCase):
    def test_merges_common_fold_predictions_and_preserves_berlin_dst_offset(self):
        source = pd.DataFrame({
            "utc_timestamp": pd.to_datetime([
                "2020-10-25 00:00:00Z",
                "2020-10-25 01:00:00Z",
                "2020-10-25 02:00:00Z",
            ], utc=True),
            "actual_load_mw": [100.0, 120.0, 110.0],
            "published_forecast_mw": [99.0, 121.0, 111.0],
        })
        forecasts = pd.DataFrame({
            "utc_timestamp": source.utc_timestamp.iloc[:2],
            "same_hour_48h": [98.0, 118.0],
            "same_hour_168h": [97.0, 117.0],
            "ridge": [101.0, 119.0],
            "gradient_boosting": [102.0, 122.0],
            "neural_network": [103.0, 123.0],
            "prophet": [104.0, 124.0],
            "published_reference": [99.0, 121.0],
        })

        with tempfile.TemporaryDirectory() as directory:
            predictions_path = Path(directory) / "predictions.csv"
            forecasts.to_csv(predictions_path, index=False)
            original = export_powerbi.FOLD_PREDICTIONS
            try:
                export_powerbi.FOLD_PREDICTIONS = predictions_path
                merged = export_powerbi.add_fold_predictions(source)
            finally:
                export_powerbi.FOLD_PREDICTIONS = original

        result = export_powerbi.add_calendar_fields(merged)
        self.assertEqual(result.has_backtest_prediction.tolist(), [True, True, False])
        self.assertEqual(result.gradient_boosting_forecast_mw.iloc[:2].tolist(), [102.0, 122.0])
        self.assertEqual(result.hour_berlin.iloc[:2].tolist(), [2, 2])
        self.assertEqual(result.utc_offset_berlin.iloc[:2].tolist(), ["+0200", "+0100"])
        self.assertEqual(result.forecast_error_mw.iloc[:2].tolist(), [-1.0, 1.0])

    def test_rejects_inconsistent_published_reference(self):
        source = pd.DataFrame({
            "utc_timestamp": pd.to_datetime(["2017-01-01 00:00:00Z"], utc=True),
            "actual_load_mw": [100.0],
            "published_forecast_mw": [99.0],
        })
        forecasts = pd.DataFrame({
            "utc_timestamp": source.utc_timestamp,
            "same_hour_48h": [98.0], "same_hour_168h": [97.0],
            "ridge": [101.0], "gradient_boosting": [102.0],
            "neural_network": [103.0], "prophet": [104.0],
            "published_reference": [98.0],
        })
        with tempfile.TemporaryDirectory() as directory:
            predictions_path = Path(directory) / "predictions.csv"
            forecasts.to_csv(predictions_path, index=False)
            original = export_powerbi.FOLD_PREDICTIONS
            try:
                export_powerbi.FOLD_PREDICTIONS = predictions_path
                with self.assertRaisesRegex(ValueError, "Published forecast values differ"):
                    export_powerbi.add_fold_predictions(source)
            finally:
                export_powerbi.FOLD_PREDICTIONS = original


if __name__ == "__main__":
    unittest.main()
