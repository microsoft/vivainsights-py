<img src="https://raw.githubusercontent.com/microsoft/vivainsights-py/main/images/vivainsights-py.png" align="right" width=15% />

[![vivainsights CI](https://github.com/microsoft/vivainsights-py/actions/workflows/python-package.yml/badge.svg)](https://github.com/microsoft/vivainsights-py/actions/workflows/python-package.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Summary

This is an Python package for analyzing and visualizing data from Microsoft Viva Insights.

Access to the Analyst Experience is required. With this library, you can generate visualizations and compute analyses in a way that adheres to the analysis best practices of the Viva Insights query outputs. 

For the full package documentation, please see [here](https://microsoft.github.io/vivainsights-py/). The **vivainsights** library is published on the [Python Package Index (PyPi)](https://pypi.org/project/vivainsights/). 

For users who prefer R to Python, we recommend the [R library counterpart](https://microsoft.github.io/vivainsights/) which mirrors the design of the Python package. 

## Visualization Gallery

`create_rank()`:

<img src="https://microsoft.github.io/vivainsights-py/_static/plots/create_rank.png" align="center" width=40% />

`create_bar()`:

<img src="https://microsoft.github.io/vivainsights-py/_static/plots/create_bar.png" align="center" width=40% />

`create_boxplot()`:

<img src="https://microsoft.github.io/vivainsights-py/_static/plots/create_boxplot.png" align="center" width=40% />

`create_line()`:

<img src="https://microsoft.github.io/vivainsights-py/_static/plots/create_line.png" align="center" width=40% />

`create_trend()`:

<img src="https://microsoft.github.io/vivainsights-py/_static/plots/create_trend.png" align="center" width=40% />

## Installation

You can install this package directly from PyPI by running the following in command prompt: 
```cmd
pip install vivainsights
```

## How to use

Once confirmed that the library is installed, here are some examples of what you can run from the package:

```python
import vivainsights as vi

pq_data = vi.load_pq_data() # load and assign in-built person query
mt_data = vi.load_mt_data() # load and assign in-built meeting query

# visualize averaged metrics per group (using person-averaging)
out_plot = vi.create_bar(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5)
out_tab = vi.create_bar(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='table')

out_plot.show() # display plot interactively, using plt
print(out_tab) # print summary table to console
```

Most functions come with an option to generate a matplotlib figure object or a summary table in the form of a Pandas DataFrame, which can be specified with the argument `return_type`. Once these output objects are generated, they can also be copied to clipboard or saved locally using the `vi.export()` function: 

```python
# export summary table results to clipboard
vi.export(out_tab)

# save plot locally as png
vi.export(out_plot, file_format = 'png')
```

The following demonstrates several other examples of visualization outputs:
```python
# Calculate counts of distinct people in each sub-population
vi.hrvar_count(data=pq_data, hrvar='Organization', return_type='plot').show()
vi.hrvar_count(data=pq_data, hrvar='Organization', return_type='table')

# Get date ranges from data frame, using 'MetricDate'
vi.extract_date_range(data=pq_data)
vi.extract_date_range(data=pq_data, return_type = "text")

# create a line chart showing average of metrics by sub-pop group over time
vi.create_line(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='plot').show()
vi.create_line(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='table')

# create a heatmap chart showing average of metrics by sub-pop group over time
vi.create_trend(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='plot').show()
vi.create_trend(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='table')

# Calculate the mean value of a metric for all groups in the dataset
vi.create_rank(
    data=pq_data,
    metric='Emails_sent',
    hrvar=['Organization', 'FunctionType', 'LevelDesignation'],
    mingroup=5,
    return_type='table'
    )

# Visualize the top and bottom values across organizational attributes
vi.create_rank(
    data=pq_data,
    metric='Emails_sent',
    hrvar=['Organization', 'FunctionType', 'LevelDesignation'],
    mingroup=5,
    return_type='plot'
    ).show()    
```

To perform analysis on a dataset from a flexible query (stored as a .csv file), there is a simple three step process:

```python
# 1. Load package
import vivainsights as vi

# 2. Load csv
pq_df = vi.import_query(x = '/data/VI_PERSON_QUERY.Csv')

# 3. Create analysis
vi.create_rank(
    data = pq_df,
    metric = 'Collaboration_hours',
    hrvar = ['Organization', 'LevelDesignation', 'FunctionType']
)
```

## Related repositories

- [Viva Insights R library](https://microsoft.github.io/vivainsights/)
- [Viva RMarkdown Report Marketplace](https://github.com/microsoft/VivaRMDReportMarketplace/)
- [Viva Insights Sample Code](https://github.com/microsoft/viva-insights-sample-code/)
- [Viva Insights Zoom Integration](https://github.com/microsoft/vivainsights_zoom_int/)
- [Viva Insights OData Query Download](https://github.com/microsoft/vivainsights-odatadl/)
- [Viva Insights R library (legacy)](https://microsoft.github.io/wpa/)


## Contributing

This project welcomes contributions and suggestions. For feature and complex bug fix contributions, it is recommended that you first discuss the proposed change with vivainsight’s maintainers before submitting the pull request. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## License

This library is licensed under the MIT License. For more information, please see the LICENSE file.
