# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Validate that required variables exist in a DataFrame.
"""
import pandas as pd

__all__ = ['check_inputs']

def check_inputs(data: pd.DataFrame, requirements: str):
  """
  Check that each variable in ``requirements`` exists as a column in ``data``.

  Parameters
  ----------
  data : pandas.DataFrame
      DataFrame to validate.
  requirements : list of str
      Column names that must be present in ``data``.

  Raises
  ------
  ValueError
      If any required variable is missing from ``data``.

  Examples
  --------
  Check that required columns are present (no error if all exist):

  >>> import vivainsights as vi
  >>> pq_data = vi.load_pq_data()
  >>> vi.check_inputs(pq_data, ["PersonId", "MetricDate"])

  This will raise a ``ValueError`` if a column is missing:

  >>> vi.check_inputs(pq_data, ["PersonId", "NonExistentColumn"])  # doctest: +SKIP
  """  
  # Check if the required variables are in the data
  # Raise an error if not
  for var in requirements:
    if var not in data.columns:
      raise ValueError(f"Error: {var} is not in the data")