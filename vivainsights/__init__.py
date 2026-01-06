"""
vivainsights - A Python package for analyzing Viva Insights data.
"""

__version__ = "0.4.2"

# --- Data Loading ---
from .pq_data import *
from .mt_data import *
from .p2p_data import *
from .g2g_data import *
from .p2g_data import *
from .p2p_data_sim import *
from .import_query import *

# --- Visualization ---
from .create_bar import *
from .create_bar_asis import *
from .create_boxplot import *
from .create_bubble import *
from .create_inc import *
from .create_line import *
from .create_lorenz import *
from .create_rank import *
from .create_sankey import *
from .create_trend import *

# --- Statistical Analysis ---
from .create_IV import *
from .create_odds_ratios import *
from .xicor import *

# --- Network Analysis ---
from .network_g2g import *
from .network_p2p import *
from .network_summary import *

# --- Identification & Segmentation ---
from .identify_churn import *
from .identify_habit import *
from .identify_holidayweeks import *
from .identify_inactiveweeks import *
from .identify_nkw import *
from .identify_outlier import *
from .identify_tenure import *
from .identify_usage_segments import *
from .keymetrics_scan import *

# --- Utilities ---
from .check_inputs import *
from .check_query import *
from .color_codes import *
from .export import *
from .extract_date_range import *
from .extract_hr import *
from .hrvar_count import *
from .totals_col import *
from .us_to_space import *