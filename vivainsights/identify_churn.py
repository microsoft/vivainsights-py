# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module identifies and counts the number of employees who have churned from the dataset.
This is done by measuring whether an employee who is present in the first `n` (n1) weeks of the data,
is also present in the last `n` (n2) weeks of the data.
An additional use case of this function is the ability to identify "new-joiners" by using the argument `flip`.
"""
import pandas as pd

def identify_churn(data: pd.DataFrame,
                   n1 = 6,
                   n2 = 6,
                   return_type: str = "message", # avoid using return as a variable name
                   flip = False,
                   date_column: str = "MetricDate",
                   date_format = "%Y-%m-%d"):
  """
  Args:
    data (dataframe): The dataframe to export
    n1: First `n` weeks of data to check for the person's presence
    n2: Last `n` weeks of data to check for the person's presence
    return_type: Type of return expected
    flip: Flag to switch between identifying churned users vs new users
    date_column: DateTime column based on which churn is calculated, defaults to MetricDate for Nova
    date_format: DateTime format in input file, defaults to YYYY-mm-dd
    
  Return:
    A different output is returned depending on the value passed to the `return_type` argument:
        `"message"`: Message on console. A diagnostic message.
        `"text"`: String. A diagnostic message.
        `"data"`: Character vector containing the the `PersonId` of employees who have been identified as churned.
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