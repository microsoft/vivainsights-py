import unittest
import gc
import pandas as pd
import matplotlib.pyplot as plt
import tracemalloc

from vivainsights.create_survival import (
    create_survival_calc,
    create_survival_viz,
    create_survival,
    _coerce_event,
)
from vivainsights.create_survival_prep import create_survival_prep
from vivainsights.pq_data import load_pq_data


def _make_surv_data(pq_data, hrvar="Organization"):
    """Helper: person-level survival data derived from pq_data."""
    return create_survival_prep(pq_data, metric="Collaboration_hours", hrvar=hrvar)


class TestCoerceEvent(unittest.TestCase):
    def test_bool(self):
        s = pd.Series([True, False, True])
        result = _coerce_event(s)
        self.assertListEqual(list(result), [1, 0, 1])

    def test_numeric(self):
        s = pd.Series([0.0, 1.5, 0, 3])
        result = _coerce_event(s)
        self.assertListEqual(list(result), [0, 1, 0, 1])

    def test_string_tokens(self):
        s = pd.Series(["true", "false", "yes", "no", "1", "0"])
        result = _coerce_event(s)
        self.assertListEqual(list(result.astype(int)), [1, 0, 1, 0, 1, 0])

    def test_string_case_insensitive(self):
        s = pd.Series(["TRUE", "False", "YES"])
        result = _coerce_event(s)
        self.assertListEqual(list(result.astype(int)), [1, 0, 1])

    def test_invalid_string_raises(self):
        s = pd.Series(["maybe", "yes"])
        with self.assertRaises(ValueError):
            _coerce_event(s)


class TestCreateSurvivalCalc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pq_data = load_pq_data()
        cls.surv_data = _make_surv_data(cls.pq_data)

    def test_returns_tuple(self):
        result = create_survival_calc(
            self.surv_data, time_col="time", event_col="event"
        )
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_survival_long_is_dataframe(self):
        survival_long, _ = create_survival_calc(
            self.surv_data, time_col="time", event_col="event"
        )
        self.assertIsInstance(survival_long, pd.DataFrame)

    def test_required_output_columns(self):
        survival_long, _ = create_survival_calc(
            self.surv_data, time_col="time", event_col="event"
        )
        for col in ["group", "time", "survival", "at_risk", "events"]:
            self.assertIn(col, survival_long.columns)

    def test_survival_bounded(self):
        survival_long, _ = create_survival_calc(
            self.surv_data, time_col="time", event_col="event"
        )
        self.assertTrue((survival_long["survival"] >= 0).all())
        self.assertTrue((survival_long["survival"] <= 1).all())

    def test_hrvar_grouping(self):
        survival_long, counts = create_survival_calc(
            self.surv_data,
            time_col="time",
            event_col="event",
            hrvar="Organization",
        )
        self.assertIn("Organization", survival_long.columns)
        self.assertGreater(survival_long["Organization"].nunique(), 1)

    def test_mingroup_filters_small_groups(self):
        # Use a very large mingroup so all groups are filtered out
        survival_long, counts = create_survival_calc(
            self.surv_data,
            time_col="time",
            event_col="event",
            hrvar="Organization",
            mingroup=999999,
        )
        self.assertTrue(survival_long.empty)

    def test_counts_series(self):
        _, counts = create_survival_calc(
            self.surv_data,
            time_col="time",
            event_col="event",
            hrvar="Organization",
        )
        self.assertIsInstance(counts, pd.Series)

    def test_missing_column_raises(self):
        with self.assertRaises(KeyError):
            create_survival_calc(
                self.surv_data, time_col="nonexistent", event_col="event"
            )


class TestCreateSurvivalViz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pq_data = load_pq_data()
        surv_data = _make_surv_data(pq_data, hrvar="Organization")
        cls.survival_long, _ = create_survival_calc(
            surv_data,
            time_col="time",
            event_col="event",
            hrvar="Organization",
        )

    def test_returns_figure(self):
        fig = create_survival_viz(self.survival_long, hrvar="Organization")
        self.assertIsInstance(fig, plt.Figure)
        plt.close("all")

    def test_empty_data_returns_figure(self):
        empty = pd.DataFrame(columns=["group", "time", "survival", "at_risk", "events"])
        fig = create_survival_viz(empty, hrvar="group")
        self.assertIsInstance(fig, plt.Figure)
        plt.close("all")


class TestCreateSurvival(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pq_data = load_pq_data()
        cls.surv_data = _make_surv_data(cls.pq_data)

    def test_returns_figure_default(self):
        tracemalloc.start()
        fig = create_survival(
            self.surv_data,
            time_col="time",
            event_col="event",
        )
        plt.close("all")
        gc.collect()
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)

    def test_returns_figure_with_hrvar(self):
        fig = create_survival(
            self.surv_data,
            time_col="time",
            event_col="event",
            hrvar="Organization",
        )
        plt.close("all")
        self.assertIsInstance(fig, plt.Figure)

    def test_return_type_table(self):
        tbl = create_survival(
            self.surv_data,
            time_col="time",
            event_col="event",
            hrvar="Organization",
            return_type="table",
        )
        self.assertIsInstance(tbl, pd.DataFrame)
        for col in ["Organization", "time", "survival"]:
            self.assertIn(col, tbl.columns)

    def test_boolean_event_col(self):
        df = self.surv_data.copy()
        df["event_bool"] = df["event"].astype(bool)
        fig = create_survival(df, time_col="time", event_col="event_bool")
        plt.close("all")
        self.assertIsInstance(fig, plt.Figure)

    def test_string_event_col(self):
        df = self.surv_data.copy()
        df["event_str"] = df["event"].map({1: "yes", 0: "no"})
        fig = create_survival(df, time_col="time", event_col="event_str")
        plt.close("all")
        self.assertIsInstance(fig, plt.Figure)


if __name__ == "__main__":
    unittest.main()
