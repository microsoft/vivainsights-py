import unittest

import vivainsights as vi

EXPECTED_PUBLIC_FUNCTIONS = frozenset(
    {
        "check_inputs",
        "check_query",
        "create_IV",
        "create_bar",
        "create_bar_asis",
        "create_boxplot",
        "create_bubble",
        "create_inc",
        "create_line",
        "create_lorenz",
        "create_odds_ratios",
        "create_radar",
        "create_rank",
        "create_sankey",
        "create_survival",
        "create_survival_prep",
        "create_trend",
        "export",
        "extract_date_range",
        "extract_hr",
        "hrvar_count",
        "hrvar_count_all",
        "identify_churn",
        "identify_datefreq",
        "identify_habit",
        "identify_holidayweeks",
        "identify_inactiveweeks",
        "identify_nkw",
        "identify_outlier",
        "identify_tenure",
        "identify_usage_segments",
        "import_query",
        "keymetrics_scan",
        "load_g2g_data",
        "load_mt_data",
        "load_p2g_data",
        "load_p2p_data",
        "load_pq_data",
        "network_g2g",
        "network_p2p",
        "network_summary",
        "p2p_data_sim",
        "totals_col",
        "us_to_space",
        "xicor",
    }
)


class TestPublicApi(unittest.TestCase):
    def test_canonical_public_functions_remain_available(self):
        missing = {
            name for name in EXPECTED_PUBLIC_FUNCTIONS
            if not callable(getattr(vi, name, None))
        }
        self.assertEqual(missing, set())


if __name__ == "__main__":
    unittest.main()
