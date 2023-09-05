# vivainsights <img src="https://raw.githubusercontent.com/microsoft/vivainsights-py/main/images/vivainsights-py.png" align="right" width=15% />

[![vivainsights CI](https://github.com/microsoft/vivainsights-py/actions/workflows/python-package.yml/badge.svg)](https://github.com/microsoft/vivainsights-py/actions/workflows/python-package.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This is an Python package for analyzing and visualizing data from Microsoft Viva Insights.

Access to the Analyst Experience is required. With this library, you can generate visualizations and compute analyses in a way that adheres to the analysis best practices of the Viva Insights query outputs. 

For the full package documentation, please see [here](https://microsoft.github.io/vivainsights-py/). The **vivainsights** library is published on the [Python Package Index (PyPi)](https://pypi.org/project/vivainsights/). 

For users who prefer R to Python, we recommend the [R library counterpart](https://microsoft.github.io/vivainsights/) which mirrors the design of the Python package. 

Example visualization output from the library (`create_rank()`):

<img src="https://microsoft.github.io/vivainsights-py/_static/plots/create_rank.png" align="center" width=40% />

## Installation

You can install **vivainsights** by running this in Command Line: 
```
pip install vivainsights
```

Alternatively, you can install the development version of **vivainsights** from this GitHub repository:
```
pip install -e git+https://github.com/microsoft/vivainsights-py#egg=vivainsights
```

To install from a specific branch, run the following command replacing branch name with `<remote-branch-name>`:
```
pip install -e git+https://github.com/microsoft/vivainsights-py@<remote-branch-name>#egg=vivainsights
```

For examples on how to create analyses and visualizations, please see the [documentation](https://microsoft.github.io/vivainsights-py/).

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
