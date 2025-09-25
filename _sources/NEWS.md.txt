# Version 0.4.1

- Improve visualization aesthetics and standardize plot sizes
- Added display behaviour for plots in `export()`
- Various bugfixes and documentation enhancements

# Version 0.4.0

- Added `create_odds_ratios()`, `identify_habit()`, and `identify_usage_segments()` as additional tools to analyse Copilot usage.
- Updated the dataset loaded with `load_pq_data()` to include metrics on Copilot.
- Added `create_bubble()` for bubble visualizations.
- Added or updated tests for `create_bubble()`, `create_line()`, `create_trend()` etc. 
- Improved diagnostic messages in `identify_holidayweeks()`. (#33)
- Improved documentation and Markdown narrative in example notebooks.

# Version 0.3.4

Added `keymetrics_scan()` for visualizing multiple metrics across an organizational attribute.

# Version 0.3.3

Added function for calculating Chatterjee coefficient.

# Version 0.3.2

Added functionality for calculating Gini coefficient and plotting the Lorenz curve.

# Version 0.3.1

Minor doc changes and additional return options. 
Bug fixes on several key plotting functions.

# Version 0.3.0

Added functionality for Information Value (IV).

# Version 0.2.4

Added stats output functionality to internal functions.

# Version 0.2.3

Fixed legend issues with `network_p2p()`, and improved test coverage. 

# Version 0.2.2

Bug fixes and improve test coverage, incl. critical bug fixes and new parameters for the ONA functions. 

See #18 for more details.

# Version 0.2.1

Bug fixes and improve test coverage.

# Version 0.2.0

The new version adds a number of organizational network analysis (ONA) functions to the library: 

- Network visualization and analysis:
    - `network_g2g()`
    - `network_p2p()`
    - `network_summary()`
    - `create_sankey()`
- Sample / simulate datasets: 
    - `p2p_data_sim()`
    - `load_g2g_data()`
    - `load_p2p_data()`

# Version 0.1.0

This is the first release of vivainsights. It includes the following features:

- Data visualization
- Data validation

The first version has been released to PyPi.