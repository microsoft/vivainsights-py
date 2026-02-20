Reference - Functions
======================

This documentation provides a comprehensive reference for all **vivainsights** functions, organized by category. Click any module name to view its full documentation.

.. _ref-visualization:

Visualization Functions
==========================

Core Visualization
------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.create_bar
   vivainsights.create_boxplot
   vivainsights.create_bubble
   vivainsights.create_line
   vivainsights.create_rank
   vivainsights.create_trend

Specialized Visualizations
--------------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.create_sankey
   vivainsights.create_lorenz
   vivainsights.create_inc
   vivainsights.create_bar_asis

Advanced Analytics Visualizations
---------------------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.create_IV
   vivainsights.create_odds_ratios

.. _ref-analysis:

Data Analysis & Identification
=================================

Employee Behavior Analysis
--------------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.identify_churn
   vivainsights.identify_tenure
   vivainsights.identify_habit
   vivainsights.identify_usage_segments

Data Quality & Anomaly Detection
---------------------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.identify_outlier
   vivainsights.identify_inactiveweeks
   vivainsights.identify_holidayweeks
   vivainsights.identify_nkw

Time & Date Analysis
---------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.identify_daterange
   vivainsights.extract_date_range

.. _ref-network:

Network Analysis
===================

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.network_g2g
   vivainsights.network_p2p
   vivainsights.network_summary

.. _ref-data:

Data Management
==================

Sample Data Sources
-------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.pq_data
   vivainsights.mt_data
   vivainsights.g2g_data
   vivainsights.p2p_data
   vivainsights.p2g_data
   vivainsights.p2p_data_sim

Data Import & Export
--------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.import_query
   vivainsights.export

.. _ref-utilities:

Utility Functions
====================

Data Processing
----------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.extract_hr
   vivainsights.hrvar_count
   vivainsights.totals_col
   vivainsights.us_to_space

Validation & Configuration
----------------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.check_inputs
   vivainsights.color_codes

Advanced Analytics
-------------------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/module.rst

   vivainsights.xicor
   vivainsights.keymetrics_scan
