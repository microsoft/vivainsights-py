# vivainsights

## Overview

Use this python library to analyze and visualize data from Microsoft Viva Insights. Access to the Analyst Experience is required. With this library, you can generate visualizations and compute analyses in a way that adheres to the analysis best practices of the Viva Insights query outputs. This library mirrors the design of its [R library counterpart](https://microsoft.github.io/vivainsights/).


## Installation

1. Clone this repository to your local drive. 
1. On PowerShell, change directory (`cd`) to the repository on your local drive, and run `python setup.py install`. This should install 'vivainsights' to your python package registry. To check whether it is installed, you can run `pip freeze` on your command prompt.

## How to use

Once confirmed that the library is installed, here are some examples of what you can run from the package:

```python
import vivainsights as vi

pq_data = vi.load_pq_data() # load and assign in-built person query
mt_data = vi.load_mt_data() # load and assign in-built meeting query

# visualize averaged metrics per group (using person-averaging)
out_plot = vi.create_bar(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5)
out_tab = vi.create_bar(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='table')

print(out_plot)
print(out_tab)

# export results to clipboard
out_tb = vi.create_bar(data=pq_data, metric='Chats_sent', hrvar='Organization', mingroup=5, return_type = 'table')
vi.export(out_tb)

# Calculate counts of distinct people in each sub-population
vi.hrvar_count(data=pq_data, hrvar='Organization', return_type='plot')
vi.hrvar_count(data=pq_data, hrvar='Organization', return_type='table')

# Get date ranges from data frame, using 'MetricDate'
vi.extract_date_range(data=pq_data)
vi.extract_date_range(data=pq_data, return_type = "text")

# create a line chart showing average of metrics by sub-pop group over time
vi.create_line(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='plot')
vi.create_line(data=pq_data, metric='Emails_sent', hrvar='Organization', mingroup=5, return_type='table')
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



## Contributing

If you're interested in contributing to this library, please see the CONTRIBUTING.md file, which can be found in the repository.

## License

This library is licensed under the MIT License. For more information, please see the LICENSE file.