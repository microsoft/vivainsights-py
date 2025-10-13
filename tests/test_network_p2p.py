import os
import glob
import re
import unittest
import warnings
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import vivainsights as vi

# Optional dependencies
try:
    import igraph as ig
    HAS_IGRAPH = True
except ImportError:
    HAS_IGRAPH = False

try:
    import plotly.graph_objects as go  # noqa: F401 (used only for type checking if impl changes)
    import plotly.io as pio
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


class TestNetworkP2P(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.p2p_data = vi.p2p_data_sim()

    def tearDown(self):
        plt.close("all")

    # ---------------------------
    # Utility helpers
    # ---------------------------
    def call_with_warnings(self, func, *args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = func(*args, **kwargs)
        return result, w

    def assert_no_unexpected_warnings(self, warnings_list, allow_any=False):
        if allow_any:
            return
        unexpected = [
            w for w in warnings_list
            if issubclass(w.category, (DeprecationWarning, FutureWarning, ResourceWarning))
        ]
        self.assertEqual(
            len(unexpected), 0,
            f"Unexpected warnings: {[str(w.message) for w in unexpected]}"
        )

    # ---------------------------
    # Core return_type tests
    # ---------------------------
    def test_return_type_table(self):
        result, w = self.call_with_warnings(
            vi.network_p2p,
            data=self.p2p_data,
            return_type="table",
            seed=123
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        self.assert_no_unexpected_warnings(w)

    def test_return_type_plot(self):
        result, w = self.call_with_warnings(
            vi.network_p2p,
            data=self.p2p_data,
            return_type="plot",
            seed=123
        )
        # Accept a variety of return patterns (None, Figure, etc.)
        possible_fig = False
        if result is None:
            possible_fig = len(plt.get_fignums()) > 0
        elif isinstance(result, matplotlib.figure.Figure):
            possible_fig = True
        elif isinstance(result, tuple):
            if any(isinstance(x, matplotlib.figure.Figure) for x in result):
                possible_fig = True
        elif hasattr(result, "figure") and isinstance(result.figure, matplotlib.figure.Figure):
            possible_fig = True

        self.assertTrue(possible_fig, "No matplotlib figure detected for return_type='plot'.")
        self.assert_no_unexpected_warnings(w)

    def test_return_type_data(self):
        result, w = self.call_with_warnings(
            vi.network_p2p,
            data=self.p2p_data,
            return_type="data",
            centrality="degree",
            seed=123
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        degree_cols = [c for c in result.columns if re.search(r"degree", c, re.IGNORECASE)]
        self.assertTrue(
            len(degree_cols) > 0,
            f"Expected degree centrality column; present columns: {result.columns}"
        )
        self.assert_no_unexpected_warnings(w)

    @unittest.skipUnless(HAS_IGRAPH, "igraph not installed - skipping network test")
    def test_return_type_network(self):
        result, w = self.call_with_warnings(
            vi.network_p2p,
            data=self.p2p_data,
            return_type="network",
            seed=123
        )
        self.assertIsInstance(result, ig.Graph)
        self.assertGreater(result.vcount(), 0)
        self.assert_no_unexpected_warnings(w)

    # ---------------------------
    # PDF path behavior
    # ---------------------------
    def test_custom_path_pdf(self):
        """
        Accept either:
        - Exact file if user passed something ending with .pdf
        - Or a generated file that starts with the provided base name.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Try without extension (acts like a prefix in many implementations)
            custom_base = os.path.join(tmpdir, "my_custom_network")
            result, w = self.call_with_warnings(
                vi.network_p2p,
                data=self.p2p_data,
                return_type="plot-pdf",
                path=custom_base,
                seed=123
            )
            # Collect newly created PDFs
            pdfs = glob.glob(os.path.join(tmpdir, "*.pdf"))
            self.assertTrue(pdfs, "No PDF created.")
            # Accept any PDF whose name starts with the base's basename
            base_name = os.path.basename(custom_base)
            matching = [p for p in pdfs if os.path.basename(p).startswith(base_name)]
            self.assertTrue(
                matching,
                f"No PDF filename starts with '{base_name}'. Found: {[os.path.basename(p) for p in pdfs]}"
            )
            if result is not None:
                self.assertTrue(
                    isinstance(result, str) and os.path.isfile(result),
                    "If function returns a path for plot-pdf, it must exist."
                )
            self.assert_no_unexpected_warnings(w)

    def test_default_path_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old = set(glob.glob(os.path.join(tmpdir, "*.pdf")))
            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result, w = self.call_with_warnings(
                    vi.network_p2p,
                    data=self.p2p_data,
                    return_type="plot-pdf",
                    path="",
                    seed=123
                )
                new = set(glob.glob("*.pdf")) - {os.path.basename(p) for p in old}
                self.assertTrue(new, "No new PDF created with default path.")
                if result is not None:
                    self.assertTrue(
                        isinstance(result, str) and os.path.isfile(result),
                        "If function returns a path for default plot-pdf, it must exist."
                    )
                self.assert_no_unexpected_warnings(w)
            finally:
                os.chdir(cwd)

    # ---------------------------
    # Community + centrality enrichment
    # ---------------------------
    @unittest.skipUnless(HAS_IGRAPH, "igraph not installed - skipping enrichment test")
    def test_enrichment_with_community_and_centrality(self):
        result, w = self.call_with_warnings(
            vi.network_p2p,
            data=self.p2p_data,
            return_type="data",
            community="leiden",
            centrality="betweenness",
            seed=123
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        community_cols = [
            c for c in result.columns
            if re.search(r"(community|cluster|leiden|membership)", c, re.IGNORECASE)
        ]
        self.assertTrue(
            community_cols,
            f"Expected a community-related column; columns: {result.columns}"
        )
        betw_cols = [c for c in result.columns if re.search(r"between", c, re.IGNORECASE)]
        self.assertTrue(
            betw_cols,
            f"Expected betweenness centrality column; columns: {result.columns}"
        )
        self.assert_no_unexpected_warnings(w)

    # ---------------------------
    # Sankey test (adjusted to prevent nbformat renderer error)
    # ---------------------------
    @unittest.skipUnless(HAS_PLOTLY, "plotly not installed - skipping sankey test")
    def test_return_type_sankey(self):
        from unittest.mock import patch
        # Prevent Plotly from invoking any renderer that needs nbformat/ipykernel
        with patch("plotly.graph_objects.Figure.show", return_value=None) as mocked_show:
            result, w = self.call_with_warnings(
                vi.network_p2p,
                data=self.p2p_data,
                return_type="sankey",
                community="multilevel",
                seed=123
            )
        self.assertIsNone(
            result,
            "Expected None since network_p2p currently does not return the Sankey figure."
        )
        mocked_show.assert_called_once()
        self.assert_no_unexpected_warnings(w, allow_any=True)

    # ---------------------------
    # Invalid return_type
    # ---------------------------
    def test_invalid_return_type(self):
        with self.assertRaises(Exception):
            vi.network_p2p(data=self.p2p_data, return_type="INVALID_TYPE", seed=123)

    # ---------------------------
    # Weighted vs unweighted vertex counts
    # ---------------------------
    @unittest.skipUnless(HAS_IGRAPH, "igraph not installed - skipping weight test")
    def test_unweighted_vs_weighted_network_vertex_count(self):
        # Create a 'weight' column explicitly since the function expects edges['weight']
        data_weighted = self.p2p_data.copy()
        # Use a simple constant or a derived metric
        data_weighted["weight"] = 1

        net_weighted, _ = self.call_with_warnings(
            vi.network_p2p,
            data=data_weighted,
            return_type="network",
            weight="weight",
            seed=123
        )
        net_unweighted, _ = self.call_with_warnings(
            vi.network_p2p,
            data=self.p2p_data,
            return_type="network",
            weight=None,
            seed=123
        )

        self.assertEqual(
            net_weighted.vcount(),
            net_unweighted.vcount(),
            "Vertex count should not change between weighted and unweighted graphs."
        )

    # ---------------------------
    # Multiple centralities smoke
    # ---------------------------
    @unittest.skipUnless(HAS_IGRAPH, "igraph not installed - skipping centrality variety test")
    def test_multiple_centralities_smoke(self):
        centralities = ["betweenness", "closeness", "degree", "eigenvector", "pagerank"]
        for cent in centralities:
            with self.subTest(centrality=cent):
                result, w = self.call_with_warnings(
                    vi.network_p2p,
                    data=self.p2p_data,
                    return_type="data",
                    centrality=cent,
                    seed=123
                )
                self.assertIsInstance(result, pd.DataFrame)
                match_cols = [c for c in result.columns if re.search(cent[:5], c, re.IGNORECASE)]
                self.assertTrue(
                    match_cols,
                    f"Expected a column referencing centrality '{cent}' in {result.columns}"
                )
                self.assert_no_unexpected_warnings(w)


if __name__ == "__main__":
    unittest.main()