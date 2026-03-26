# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
create_survival_prep: Convert Standard Person Query panel data into person-level
survival analysis format (time-to-event + event indicator).

This is typically used as the first step before calling `create_survival()`.

Example
-------
>>> import vivainsights as vi
>>> from vivainsights.create_survival_prep import create_survival_prep
>>>
>>> pq_data = vi.load_pq_data()
>>> surv_data = create_survival_prep(
...     data=pq_data,
...     metric="Copilot_actions_taken_in_Teams",
... )
>>> surv_data.head()

With a custom event condition and HR attribute:

>>> surv_data = create_survival_prep(
...     data=pq_data,
...     metric="Copilot_actions_taken_in_Teams",
...     event_condition=lambda x: x >= 10,
...     hrvar="LevelDesignation",
... )

Pass the output directly to create_survival:

>>> import vivainsights as vi
>>> pq_data = vi.load_pq_data()
>>> surv_data = vi.create_survival_prep(pq_data, metric="Copilot_actions_taken_in_Teams")
>>> fig = vi.create_survival(surv_data, time_col="time", event_col="event", hrvar="Organization")
"""

from typing import Callable, Optional

import pandas as pd

__all__ = ["create_survival_prep"]


def create_survival_prep(
    data: pd.DataFrame,
    metric: str,
    event_condition: Callable[[pd.Series], pd.Series] = lambda x: x > 0,
    hrvar: Optional[str] = "Organization",
    id_col: str = "PersonId",
    date_col: str = "MetricDate",
) -> pd.DataFrame:
    """
    Name
    ----
    create_survival_prep

    Description
    -----------
    Convert a Standard Person Query panel dataset (multiple rows per person, one per
    period/week) into a person-level survival analysis table suitable for use with
    `create_survival()` or `create_survival_calc()`.

    For each person the function determines:

    - **time**: the number of observed periods until the event first occurred, or the
      total number of periods observed if the event never occurred (censored).
    - **event**: 1 if ``event_condition`` was satisfied in at least one period,
      0 if censored (condition never met within the observation window).

    The HR attribute column (`hrvar`) is carried through using the most recently
    observed value per person (last row after sorting by `date_col`).

    Parameters
    ----------
    data : pd.DataFrame
        Standard Person Query panel data. One row per person per period.
    metric : str
        Numeric metric column to evaluate against `event_condition`.
    event_condition : callable, default ``lambda x: x > 0``
        A function that accepts a pandas Series of metric values and returns a
        boolean Series. The event is considered to have occurred at the first
        period where this condition is True.

        Examples:

        - ``lambda x: x > 0``   — any non-zero activity (default)
        - ``lambda x: x >= 10`` — at least 10 actions in a period
    hrvar : str or None, default "Organization"
        HR attribute column to carry through into the output (most recent observed
        value per person). Set to None to omit.
    id_col : str, default "PersonId"
        Column uniquely identifying each person.
    date_col : str, default "MetricDate"
        Date/period column used to sort rows chronologically before computing the
        time-to-event. If absent, the existing row order is preserved.

    Returns
    -------
    pd.DataFrame
        One row per person with columns:

        - ``id_col`` (e.g. "PersonId")
        - ``"time"`` — periods until event, or total observed periods if censored
        - ``"event"`` — 1 (event occurred) or 0 (censored)
        - ``hrvar`` column, if supplied and present in ``data``

    Raises
    ------
    KeyError
        If `metric` or `id_col` is not found in `data`.
    ValueError
        If `event_condition` does not return a boolean-compatible Series.

    Notes
    -----
    This function mirrors ``create_survival_prep()`` in the R vivainsights package.
    The typical workflow is::

        surv_data = create_survival_prep(pq_data, metric="Copilot_actions_taken_in_Teams")
        fig = create_survival(surv_data, time_col="time", event_col="event")

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> surv_data = create_survival_prep(
    ...     data=pq_data,
    ...     metric="Copilot_actions_taken_in_Teams",
    ... )
    >>> surv_data.head()
    """
    # Validate required columns
    missing = [c for c in [id_col, metric] if c not in data.columns]
    if missing:
        raise KeyError(f"Missing required column(s): {missing}")

    # Validate event_condition
    try:
        test_result = event_condition(data[metric].iloc[:1])
        if not hasattr(test_result, "dtype"):
            raise TypeError("event_condition must return a pandas Series.")
        bool(test_result.iloc[0])
    except (TypeError, AttributeError) as exc:
        raise ValueError(
            "`event_condition` must accept a pandas Series and return a boolean-compatible "
            f"Series. Got error: {exc}"
        ) from exc

    # Sort chronologically if date column exists
    df = data.copy()
    if date_col in df.columns:
        df = df.sort_values([id_col, date_col]).reset_index(drop=True)

    # Apply event_condition
    df["_event_flag"] = event_condition(df[metric]).astype(bool)

    # 1-based chronological period number within each person
    df["_period"] = df.groupby(id_col, sort=False).cumcount() + 1

    # Whether the event ever occurred per person
    event_series = df.groupby(id_col, sort=False)["_event_flag"].any().astype(int)

    # First period where event occurred (present only for people who had an event)
    first_event_period = (
        df.loc[df["_event_flag"]]
        .groupby(id_col, sort=False)["_period"]
        .min()
    )

    # Total observed periods per person (used for censored observations)
    total_periods = df.groupby(id_col, sort=False)["_period"].max()

    # time = first event period if event occurred, else total observed periods
    time_series = first_event_period.combine_first(total_periods).astype(int)

    result = pd.DataFrame({"time": time_series, "event": event_series})
    result.index.name = id_col
    result = result.reset_index()

    # Carry through hrvar: most recent non-null value per person
    if hrvar and hrvar in df.columns:
        hrvar_series = (
            df.dropna(subset=[hrvar])
            .groupby(id_col, sort=False)[hrvar]
            .last()
            .rename(hrvar)
        )
        result = result.merge(hrvar_series, on=id_col, how="left")

    # Column ordering: id, time, event, [hrvar]
    cols = [id_col, "time", "event"]
    if hrvar and hrvar in result.columns:
        cols.append(hrvar)

    return result[cols].reset_index(drop=True)
