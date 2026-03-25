# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Identify and count employees who have churned from or joined the dataset.

This is done by measuring whether an employee who is present in the first `n` (n1) weeks of the data,
is also present in the last `n` (n2) weeks of the data.
An additional use case of this function is the ability to identify "new-joiners" by using the argument `flip`.
"""

__all__ = ['identify_churn']

import pandas as pd

def identify_churn(data: pd.DataFrame,
                   n1 = 6,
                   n2 = 6,
                   return_type: str = "message", # avoid using return as a variable name
                   flip = False,
                   date_column: str = "MetricDate",
                   date_format = "%Y-%m-%d"):
  """Identify employees who have churned from or joined the dataset.

  Measures whether employees present in the first *n1* weeks are still
  present in the last *n2* weeks.  Set ``flip=True`` to identify
  new joiners instead of churned employees.

  Parameters
  ----------
  data : pandas.DataFrame
      Person query data.
  n1 : int, default 6
      Number of initial weeks to check for presence.
  n2 : int, default 6
      Number of final weeks to check for presence.
  return_type : str, default "message"
      ``"message"`` prints a diagnostic, ``"text"`` returns it as a
      string, ``"data"`` returns the set of matching ``PersonId`` values.
  flip : bool, default False
      If ``True``, identify new joiners rather than churned employees.
  date_column : str, default "MetricDate"
      Name of the date column.
  date_format : str, default "%Y-%m-%d"
      ``strftime`` format of dates in *date_column*.

  Returns
  -------
  None, str, or set
      A printed message, a diagnostic string, or a set of ``PersonId``
      values depending on *return_type*.

  Examples
  --------
  Return a diagnostic text summary:

  >>> import vivainsights as vi
  >>> pq_data = vi.load_pq_data()
  >>> vi.identify_churn(pq_data, return_type="text")

  Return the set of churned PersonIds:

  >>> vi.identify_churn(pq_data, return_type="data")

  Flip the logic to detect employees who appear only in later weeks:

  >>> vi.identify_churn(pq_data, flip=True, return_type="text")

  Customize the number of boundary weeks to compare:

  >>> vi.identify_churn(pq_data, n1=3, n2=3, return_type="text")
  """

  data[date_column] = pd.to_datetime(data[date_column], format = date_format) # Ensure correct format

  unique_dates = data[date_column].unique() # Array of unique dates

  # First and last n weeks
  firstnweeks = sorted(unique_dates)[:n1]
  lastnweeks = sorted(unique_dates, reverse = True)[:n2]

  # People in the first week
  first_peeps = data[data[date_column].isin(firstnweeks)]['PersonId'].unique()

  # People in the last week
  final_peeps = data[data[date_column].isin(lastnweeks)]['PersonId'].unique()

  if flip == False:

    # In first, not in last
    churner_id = set(first_peeps) - set(final_peeps)

    # Message
    printMessage = (f"Churn:\nThere are {len(churner_id)} employees from "
                    f"{min(firstnweeks).date()} to {max(firstnweeks).date()} "
                    f"({n1} weeks) who are no longer present in "
                    f"{min(lastnweeks).date()} to {max(lastnweeks).date()} "
                    f"({n2} weeks).")

  elif flip == True:

    # In last, not in first
    # new joiners
    churner_id = set(final_peeps) - set(first_peeps)

    # Message
    printMessage = (f"New joiners:\nThere are {len(churner_id)} employees from "
                    f"{min(lastnweeks).date()} to {max(lastnweeks).date()} "
                    f"({n2} weeks) who were not present in "
                    f"{min(firstnweeks).date()} to {max(firstnweeks).date()} "
                    f"({n1} weeks).")

  else:
    raise ValueError("Invalid argument for `flip`")

  if return_type == "message":
    print(printMessage)

  elif return_type == "text":
    return printMessage

  elif return_type == "data":
    return churner_id

  else:
    raise ValueError("Invalid `return`")