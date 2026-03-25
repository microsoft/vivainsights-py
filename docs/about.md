**vivainsights** is a Python package for analyzing and visualizing data from Microsoft Viva Insights.

Access to the Viva Insights Analyst Experience is required. With this library, you can generate visualizations and compute analyses in a way that adheres to the analysis best practices of the Viva Insights query outputs. 

This library is available on the [Python Package Index (PyPi)](https://pypi.org/project/vivainsights/). For users who prefer R to Python, we recommend the [R library counterpart](https://microsoft.github.io/vivainsights/) which mirrors the design of the Python package. 

* [GitHub repository](https://github.com/microsoft/vivainsights-py/)
* [Microsoft Viva Insights product page](https://www.microsoft.com/en-us/microsoft-viva/insights)
* [R counterpart of this package](https://microsoft.github.io/vivainsights/)
* [Module reference](https://microsoft.github.io/vivainsights-py/modules.html)

## Installation

You can install **vivainsights** from [PyPI](https://pypi.org/project/vivainsights/) using pip:

```bash
pip install vivainsights
```

To upgrade to the latest version:

```bash
pip install --upgrade vivainsights
```

If you want to install with optional dependencies for development or documentation, you can use:

```bash
pip install vivainsights[dev]
```
To get started, we recommend checking out the [demo Jupyter notebook](https://microsoft.github.io/vivainsights-py/demo-vivainsights-py.html) and the code examples below. You can also find more details in our [GitHub repository](https://github.com/microsoft/vivainsights-py/).

## Quick start

Once the library is installed, you can get started in just a few lines:

```python
import vivainsights as vi

# Load a built-in sample person query dataset
pq_data = vi.load_pq_data()

# Create a bar chart of average metrics by group
vi.create_bar(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5)
```

Most functions accept a `return_type` argument to switch between a plot (`'plot'`) and a summary table (`'table'`) as a Pandas DataFrame. Use `vi.export()` to save outputs to clipboard or to a local file.

For a comprehensive walkthrough — including trend analysis, ranking, network visualization, and more — see the **[demo notebook](https://microsoft.github.io/vivainsights-py/demo-vivainsights-py.html)**.

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
