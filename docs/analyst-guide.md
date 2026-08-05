# Analyst Guide

## Understand the data contract

Person query exports consistently use `PersonId` for the person identifier and
`MetricDate` for the observation date. Other column names can depend on:

- the query and selected metrics;
- the Viva Insights product version;
- the language locale used when the export was created;
- organizational attributes configured by the analyst.

Treat metrics and organizational attributes as fulfilling **semantic roles**
rather than assuming universal English names:

| Role | Typical package argument | Canonical name after import |
|---|---|---|
| Person identifier | Fixed person-query field | `PersonId` |
| Observation date | Fixed person-query field | `MetricDate` |
| Analysis measure | `metric` | Caller-selected |
| Organizational attribute | `hrvar` | Caller-selected |
| Network endpoints | `primary`, `secondary` | Caller-selected |

Examples and sample data use common English metric and organizational-attribute
names for readability. Those variable columns are examples, not a schema
guarantee.

## Import a query

Import a person query directly:

```python
import vivainsights as vi

data = vi.import_query("query.csv")
```

`import_query()` preserves the stable `PersonId` and `MetricDate` names and
cleans spaces and special characters in other column names.

## Validate before analysis

Inspect available organizational attributes and validate required fields:

```python
vi.extract_hr(data, return_type="suggestion")
vi.check_inputs(data, ["PersonId", "MetricDate"])
vi.check_inputs(data, ["Emails_sent", "Organization"])
```

Pass the actual columns in your export to analytical functions:

```python
summary = vi.create_bar(
    data,
    metric="Emails_sent",
    hrvar="Organization",
    return_type="table",
)
```

If your export uses localized or custom names, pass those names instead:

```python
summary = vi.create_bar(
    data,
    metric="E-mails_envoyés",
    hrvar="Organisation",
    return_type="table",
)
```

## Choose an output

Many functions follow the R package convention of offering several output
forms. Python uses `return_type` because `return` is a Python keyword.

```python
table = vi.create_bar(
    data,
    metric="Emails_sent",
    hrvar="Organization",
    return_type="table",
)

figure = vi.create_bar(
    data,
    metric="Emails_sent",
    hrvar="Organization",
    return_type="plot",
)
```

Consult each function's API page for its supported values; not every function
offers the same output forms.

## Work with evolving exports

When a product update changes a metric name:

1. inspect the export's columns;
2. identify which column now fulfills the analytical role;
3. pass that column explicitly to `metric`, `hrvar`, or the relevant selector;
4. avoid renaming every metric to match an old sample unless a shared internal
   data contract is useful for your project.

This keeps analysis code explicit while avoiding package-level assumptions
about future Viva Insights schemas.
