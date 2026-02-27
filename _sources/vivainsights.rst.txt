Reference - Functions
======================

This documentation provides a comprehensive reference for all **vivainsights** functions, organized by category. Click any module name to view its full documentation.

.. toctree::
   :hidden:
   :glob:

   _api/*

.. _ref-visualization:

Visualization Functions
==========================

Core Visualization
------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.create_bar <_api/vivainsights.create_bar>`
     - Calculate and visualize the mean of a metric by organizational group.
   * - :doc:`vivainsights.create_boxplot <_api/vivainsights.create_boxplot>`
     - Create boxplot visualizations of metric distributions by organizational group.
   * - :doc:`vivainsights.create_bubble <_api/vivainsights.create_bubble>`
     - Create a bubble chart visualization of two metrics by organizational group.
   * - :doc:`vivainsights.create_line <_api/vivainsights.create_line>`
     - Visualize the average of a metric by sub-population over time as a line chart.
   * - :doc:`vivainsights.create_rank <_api/vivainsights.create_rank>`
     - Rank all groups across HR attributes for a selected Viva Insights metric.
   * - :doc:`vivainsights.create_trend <_api/vivainsights.create_trend>`
     - Create a week-by-week heatmap of a selected Viva Insights metric.

Specialized Visualizations
--------------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.create_sankey <_api/vivainsights.create_sankey>`
     - Create a Sankey chart from a two-column count table.
   * - :doc:`vivainsights.create_lorenz <_api/vivainsights.create_lorenz>`
     - Calculate the Gini coefficient and plot the Lorenz curve for a given metric.
   * - :doc:`vivainsights.create_inc <_api/vivainsights.create_inc>`
     - Analyze the proportion of a population above or below a metric threshold.
   * - :doc:`vivainsights.create_bar_asis <_api/vivainsights.create_bar_asis>`
     - Create a bar chart with customizable options and no pre-aggregation.

Advanced Analytics Visualizations
---------------------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.create_IV <_api/vivainsights.create_IV>`
     - Calculate Information Value (IV) and Weight of Evidence (WOE) for predictors.
   * - :doc:`vivainsights.create_odds_ratios <_api/vivainsights.create_odds_ratios>`
     - Calculate odds ratios for ordinal metrics against a specified outcome.

.. _ref-analysis:

Data Analysis & Identification
=================================

Employee Behavior Analysis
--------------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.identify_churn <_api/vivainsights.identify_churn>`
     - Identify and count employees who have churned from or joined the dataset.
   * - :doc:`vivainsights.identify_tenure <_api/vivainsights.identify_tenure>`
     - Calculate and summarize employee tenure based on hire and metric dates.
   * - :doc:`vivainsights.identify_habit <_api/vivainsights.identify_habit>`
     - Identify recurring behavioral habits from Viva Insights metrics.
   * - :doc:`vivainsights.identify_usage_segments <_api/vivainsights.identify_usage_segments>`
     - Segment employees into usage-based groups from collaboration metrics.

Data Quality & Anomaly Detection
---------------------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.identify_outlier <_api/vivainsights.identify_outlier>`
     - Identify outlier weeks using z-scores for a selected metric.
   * - :doc:`vivainsights.identify_inactiveweeks <_api/vivainsights.identify_inactiveweeks>`
     - Identify weeks where collaboration hours fall far below the mean.
   * - :doc:`vivainsights.identify_holidayweeks <_api/vivainsights.identify_holidayweeks>`
     - Detect holiday weeks by scanning for anomalous collaboration hours.
   * - :doc:`vivainsights.identify_nkw <_api/vivainsights.identify_nkw>`
     - Identify non-knowledge workers based on collaboration activity thresholds.

Time & Date Analysis
---------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.identify_daterange <_api/vivainsights.identify_daterange>`
     - Identify whether a date column has daily, weekly, or monthly frequency.
   * - :doc:`vivainsights.extract_date_range <_api/vivainsights.extract_date_range>`
     - Extract the minimum and maximum date range from a dataset.

.. _ref-network:

Network Analysis
===================

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.network_g2g <_api/vivainsights.network_g2g>`
     - Create a network plot from a group-to-group query.
   * - :doc:`vivainsights.network_p2p <_api/vivainsights.network_p2p>`
     - Perform person-to-person network analysis and visualization.
   * - :doc:`vivainsights.network_summary <_api/vivainsights.network_summary>`
     - Summarize node centrality statistics from an igraph network object.

.. _ref-data:

Data Management
==================

Sample Data Sources
-------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.pq_data <_api/vivainsights.pq_data>`
     - Load a sample person query dataset.
   * - :doc:`vivainsights.mt_data <_api/vivainsights.mt_data>`
     - Load a sample meeting query dataset.
   * - :doc:`vivainsights.g2g_data <_api/vivainsights.g2g_data>`
     - Load a sample group-to-group query dataset.
   * - :doc:`vivainsights.p2p_data <_api/vivainsights.p2p_data>`
     - Load a sample person-to-person query dataset.
   * - :doc:`vivainsights.p2g_data <_api/vivainsights.p2g_data>`
     - Load a sample person-to-group query dataset.
   * - :doc:`vivainsights.p2p_data_sim <_api/vivainsights.p2p_data_sim>`
     - Simulate a person-to-person network using the Watts-Strogatz model.

Data Import & Export
--------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.import_query <_api/vivainsights.import_query>`
     - Import a Viva Insights query from a CSV file with optimized variable types.
   * - :doc:`vivainsights.export <_api/vivainsights.export>`
     - Display and export data frames and plot objects to various formats.

.. _ref-utilities:

Utility Functions
====================

Data Processing
----------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.extract_hr <_api/vivainsights.extract_hr>`
     - Extract HR or organizational attribute columns from a Viva Insights dataset.
   * - :doc:`vivainsights.hrvar_count <_api/vivainsights.hrvar_count>`
     - Count the number of distinct persons by organizational group.
   * - :doc:`vivainsights.totals_col <_api/vivainsights.totals_col>`
     - Add a totals column with a specified value to a DataFrame.
   * - :doc:`vivainsights.us_to_space <_api/vivainsights.us_to_space>`
     - Replace underscores with spaces in a given string.

Validation & Configuration
----------------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.check_inputs <_api/vivainsights.check_inputs>`
     - Validate that required variables exist in a DataFrame.
   * - :doc:`vivainsights.color_codes <_api/vivainsights.color_codes>`
     - Define color palettes and an Enum class for standard vivainsights colors.

Advanced Analytics
-------------------

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - :doc:`vivainsights.xicor <_api/vivainsights.xicor>`
     - Calculate the Chatterjee (xi) correlation coefficient for a given metric.
   * - :doc:`vivainsights.keymetrics_scan <_api/vivainsights.keymetrics_scan>`
     - Generate a heatmap or summary table scanning key Viva Insights metrics.
