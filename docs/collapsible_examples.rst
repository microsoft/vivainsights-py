.. _collapsible-docs-example:

Collapsible Documentation Examples
==================================

This file shows different ways to create collapsible documentation sections.

Option 1: Simple Dropdowns
--------------------------

.. dropdown:: Basic Function Documentation
   :color: primary

   .. autofunction:: vivainsights.create_bar
      :no-index:

.. dropdown:: Function with Description
   :color: secondary
   :open:

   **create_bubble** - Creates bubble plots for dual-metric analysis
   
   .. autofunction:: vivainsights.create_bubble
      :no-index:

Option 2: Grouped Dropdowns
---------------------------

.. dropdown:: Core Visualization Functions
   :color: info
   :icon: graph

   Functions for creating basic visualizations:

   .. dropdown:: create_bar
      :color: light

      .. autofunction:: vivainsights.create_bar
         :no-index:

   .. dropdown:: create_boxplot
      :color: light

      .. autofunction:: vivainsights.create_boxplot
         :no-index:

   .. dropdown:: create_bubble
      :color: light

      .. autofunction:: vivainsights.create_bubble
         :no-index:

Option 3: Tabs for Categories
-----------------------------

.. tab-set::

    .. tab-item:: Visualization
        :class-label: sd-font-weight-bold        .. dropdown:: create_bar
           :color: primary

           .. autofunction:: vivainsights.create_bar
              :no-index:

        .. dropdown:: create_boxplot
           :color: primary

           .. autofunction:: vivainsights.create_boxplot
              :no-index:

    .. tab-item:: Analysis
        :class-label: sd-font-weight-bold

        .. dropdown:: identify_churn
           :color: warning

           .. autofunction:: vivainsights.identify_churn
              :no-index:

        .. dropdown:: identify_outlier
           :color: warning

           .. autofunction:: vivainsights.identify_outlier
              :no-index:

Option 4: Cards with Dropdowns
------------------------------

.. grid:: 2

    .. grid-item-card:: Core Visualizations
        :class-header: bg-light
        :margin: 2

        .. dropdown:: Available Functions
           :color: primary

           * ``create_bar()`` - Bar charts
           * ``create_boxplot()`` - Distribution plots  
           * ``create_bubble()`` - Bubble plots
           * ``create_line()`` - Line charts

    .. grid-item-card:: Data Analysis
        :class-header: bg-light
        :margin: 2

        .. dropdown:: Available Functions
           :color: success

           * ``identify_churn()`` - Turnover analysis
           * ``identify_outlier()`` - Anomaly detection
           * ``identify_tenure()`` - Tenure analysis

Option 5: Summary Tables with Dropdowns
---------------------------------------

.. list-table:: Function Quick Reference
   :widths: 30 70
   :header-rows: 1

   * - Function
     - Details   * - ``create_bar()``
     - .. dropdown:: View Documentation
          :color: primary

          .. autofunction:: vivainsights.create_bar
             :no-index:
   * - ``create_bubble()``
     - .. dropdown:: View Documentation
          :color: primary

          .. autofunction:: vivainsights.create_bubble
             :no-index:
