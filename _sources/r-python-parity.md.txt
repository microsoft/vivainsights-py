# Moving between R and Python

The Python and R packages share analytical concepts and function names wherever
the languages permit. The goal is familiar workflows, not byte-for-byte API
identity.

## Common conventions

| Concept | Python | R |
|---|---|---|
| Package alias | `import vivainsights as vi` | `library(vivainsights)` |
| Output selector | `return_type="table"` | `return="table"` |
| Data frame | `pandas.DataFrame` | `data.frame` or tibble |
| Plot | Matplotlib, Seaborn, or Plotly object | ggplot object |
| Missing value | `None` or `numpy.nan` | `NULL` or `NA` |

Python uses `return_type` because `return` is a reserved keyword. Supported
values are documented per function and generally mirror the corresponding R
function.

## Shared analytical functions

The following established functions have direct or close counterparts:

| Analysis family | Python and R function names |
|---|---|
| Core visualizations | `create_bar`, `create_boxplot`, `create_bubble`, `create_line`, `create_rank`, `create_trend` |
| Specialized visualizations | `create_inc`, `create_lorenz`, `create_radar`, `create_sankey`, `create_survival` |
| Data validation | `check_query`, `extract_date_range`, `extract_hr`, `hrvar_count` |
| Segmentation | `identify_churn`, `identify_holidayweeks`, `identify_inactiveweeks`, `identify_outlier`, `identify_usage_segments` |
| Network analysis | `network_g2g`, `network_p2p`, `network_summary` |
| Data access | `import_query`, `load_pq_data`, `load_g2g_data`, `load_p2p_data` |

The R package may contain newer functions that have not yet been implemented in
Python. Check the [R reference](https://microsoft.github.io/vivainsights/reference/index.html)
and the {doc}`Python reference <modules>` for the current surfaces.

## Equivalent example

Python:

```python
import vivainsights as vi

data = vi.load_pq_data()
result = vi.create_bar(
    data,
    metric="Collaboration_hours",
    hrvar="Organization",
    return_type="table",
)
```

R:

```r
library(vivainsights)

data <- pq_data
result <- create_bar(
  data,
  metric = "Collaboration_hours",
  hrvar = "Organization",
  return = "table"
)
```

## Intentional differences

- Python follows Python naming and keyword rules.
- Plot object types differ between ecosystems.
- Python functions generally return pandas objects; R functions generally
  return data frames or tibbles.
- A function available in one package may arrive later in the other.

When porting an analysis, first match the function's analytical purpose and
selected columns, then account for these language-specific differences.
