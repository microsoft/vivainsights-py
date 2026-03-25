import unittest
import gc
import pandas as pd
import matplotlib.pyplot as plt
import tracemalloc

from vivainsights.create_radar import (
    create_radar_calc,
    create_radar_viz,
    create_radar,
)
from vivainsights.pq_data import load_pq_data


_METRICS = ["Collaboration_hours", "Meeting_and_call_hours", "Email_hours", "Internal_network_size"]


class TestCreateRadarCalc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pq_data = load_pq_data()

    def test_returns_tuple(self):
        result = create_radar_calc(
            self.pq_data, metrics=_METRICS, hrvar="Organization"
        )
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_table_is_dataframe(self):
        table, _ = create_radar_calc(
            self.pq_data, metrics=_METRICS, hrvar="Organization"
        )
        self.assertIsInstance(table, pd.DataFrame)

    def test_table_has_metric_columns(self):
        table, _ = create_radar_calc(
            self.pq_data, metrics=_METRICS, hrvar="Organization"
        )
        for m in _METRICS:
            self.assertIn(m, table.columns)

    def test_table_has_hrvar_column(self):
        table, _ = create_radar_calc(
            self.pq_data, metrics=_METRICS, hrvar="Organization"
        )
        self.assertIn("Organization", table.columns)

    def test_index_mode_total_near_100(self):
        # Total indexing: overall mean should map to ~100
        table, _ = create_radar_calc(
            self.pq_data,
            metrics=_METRICS,
            hrvar="Organization",
            index_mode="total",
        )
        self.assertTrue((table[_METRICS] > 0).all().all())

    def test_index_mode_none_raw_values(self):
        table_none, _ = create_radar_calc(
            self.pq_data, metrics=_METRICS, hrvar="Organization", index_mode="none"
        )
        table_raw, _ = create_radar_calc(
            self.pq_data,
            metrics=_METRICS,
            hrvar="Organization",
            index_mode="none",
            agg="mean",
        )
        # Raw values should be numeric and positive
        self.assertTrue((table_raw[_METRICS] >= 0).all().all())

    def test_index_mode_minmax_in_range(self):
        table, _ = create_radar_calc(
            self.pq_data, metrics=_METRICS, hrvar="Organization", index_mode="minmax"
        )
        self.assertTrue((table[_METRICS] >= 0).all().all())
        self.assertTrue((table[_METRICS] <= 100.01).all().all())

    def test_index_mode_ref_group(self):
        orgs = self.pq_data["Organization"].dropna().unique()
        ref = str(orgs[0])
        table, _ = create_radar_calc(
            self.pq_data,
            metrics=_METRICS,
            hrvar="Organization",
            index_mode="ref_group",
            index_ref_group=ref,
        )
        ref_row = table[table["Organization"] == ref]
        if not ref_row.empty:
            for m in _METRICS:
                self.assertAlmostEqual(float(ref_row[m].iloc[0]), 100.0, places=1)

    def test_mingroup_removes_small_groups(self):
        table, _ = create_radar_calc(
            self.pq_data,
            metrics=_METRICS,
            hrvar="Organization",
            mingroup=999999,
        )
        self.assertTrue(table.empty)

    def test_missing_metric_raises(self):
        with self.assertRaises(KeyError):
            create_radar_calc(
                self.pq_data,
                metrics=["NonExistentMetric"],
                hrvar="Organization",
            )

    def test_ref_group_not_found_raises(self):
        with self.assertRaises(ValueError):
            create_radar_calc(
                self.pq_data,
                metrics=_METRICS,
                hrvar="Organization",
                index_mode="ref_group",
                index_ref_group="GroupThatDoesNotExist",
            )

    def test_median_agg(self):
        table, _ = create_radar_calc(
            self.pq_data, metrics=_METRICS, hrvar="Organization", agg="median"
        )
        self.assertFalse(table.empty)


class TestCreateRadarViz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pq_data = load_pq_data()
        cls.table, _ = create_radar_calc(
            pq_data, metrics=_METRICS, hrvar="Organization"
        )

    def test_returns_figure(self):
        fig = create_radar_viz(self.table, metrics=_METRICS, hrvar="Organization")
        self.assertIsInstance(fig, plt.Figure)
        plt.close("all")

    def test_title_and_subtitle(self):
        fig = create_radar_viz(
            self.table,
            metrics=_METRICS,
            hrvar="Organization",
            title="Test Title",
            subtitle="Test Subtitle",
        )
        self.assertIsInstance(fig, plt.Figure)
        plt.close("all")

    def test_empty_data_raises(self):
        empty = pd.DataFrame(columns=["Organization"] + _METRICS)
        with self.assertRaises(ValueError):
            create_radar_viz(empty, metrics=_METRICS, hrvar="Organization")


class TestCreateRadar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pq_data = load_pq_data()

    def test_returns_figure_default(self):
        tracemalloc.start()
        fig = create_radar(
            self.pq_data,
            metrics=_METRICS,
            hrvar="Organization",
        )
        plt.close("all")
        gc.collect()
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)

    def test_return_type_table(self):
        tbl = create_radar(
            self.pq_data,
            metrics=_METRICS,
            hrvar="Organization",
            return_type="table",
        )
        self.assertIsInstance(tbl, pd.DataFrame)
        self.assertIn("Organization", tbl.columns)
        for m in _METRICS:
            self.assertIn(m, tbl.columns)

    def test_index_mode_minmax(self):
        fig = create_radar(
            self.pq_data,
            metrics=_METRICS,
            hrvar="Organization",
            index_mode="minmax",
        )
        plt.close("all")
        self.assertIsInstance(fig, plt.Figure)

    def test_different_hrvar(self):
        fig = create_radar(
            self.pq_data,
            metrics=_METRICS,
            hrvar="LevelDesignation",
        )
        plt.close("all")
        self.assertIsInstance(fig, plt.Figure)

    def test_invalid_hrvar_raises(self):
        with self.assertRaises(KeyError):
            create_radar(
                self.pq_data,
                metrics=_METRICS,
                hrvar="NonExistentColumn",
            )


if __name__ == "__main__":
    unittest.main()
