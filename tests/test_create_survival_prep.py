import unittest
import gc
import pandas as pd
import tracemalloc

from vivainsights.create_survival_prep import create_survival_prep
from vivainsights.pq_data import load_pq_data


class TestCreateSurvivalPrep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pq_data = load_pq_data()

    def test_returns_dataframe(self):
        result = create_survival_prep(self.pq_data, metric="Collaboration_hours")
        self.assertIsInstance(result, pd.DataFrame)

    def test_one_row_per_person(self):
        result = create_survival_prep(self.pq_data, metric="Collaboration_hours")
        n_people = self.pq_data["PersonId"].nunique()
        self.assertEqual(len(result), n_people)

    def test_required_columns_present(self):
        result = create_survival_prep(self.pq_data, metric="Collaboration_hours")
        for col in ["PersonId", "time", "event", "Organization"]:
            self.assertIn(col, result.columns)

    def test_event_is_binary(self):
        result = create_survival_prep(self.pq_data, metric="Collaboration_hours")
        self.assertTrue(result["event"].isin([0, 1]).all())

    def test_time_is_positive(self):
        result = create_survival_prep(self.pq_data, metric="Collaboration_hours")
        self.assertTrue((result["time"] >= 1).all())

    def test_hrvar_none_omits_column(self):
        result = create_survival_prep(
            self.pq_data, metric="Collaboration_hours", hrvar=None
        )
        self.assertNotIn("Organization", result.columns)
        self.assertListEqual(list(result.columns), ["PersonId", "time", "event"])

    def test_custom_event_condition(self):
        # High threshold — most people should be censored (event=0)
        result = create_survival_prep(
            self.pq_data,
            metric="Collaboration_hours",
            event_condition=lambda x: x > 999999,
        )
        self.assertTrue((result["event"] == 0).all())

    def test_custom_hrvar(self):
        result = create_survival_prep(
            self.pq_data, metric="Collaboration_hours", hrvar="LevelDesignation"
        )
        self.assertIn("LevelDesignation", result.columns)
        self.assertNotIn("Organization", result.columns)

    def test_missing_metric_raises(self):
        with self.assertRaises(KeyError):
            create_survival_prep(self.pq_data, metric="NonExistentMetric")

    def test_invalid_event_condition_raises(self):
        with self.assertRaises((ValueError, TypeError)):
            create_survival_prep(
                self.pq_data,
                metric="Collaboration_hours",
                event_condition=lambda x: "not_a_series",
            )

    def test_memory(self):
        tracemalloc.start()
        result = create_survival_prep(self.pq_data, metric="Collaboration_hours")
        del result
        gc.collect()
        tracemalloc.stop()


if __name__ == "__main__":
    unittest.main()
