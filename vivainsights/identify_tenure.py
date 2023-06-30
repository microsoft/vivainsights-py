# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The `identify_tenure` function calculates and summarizes employee tenure based on hire and metric
dates, and provides various options for returning the results.

:param data: A pandas DataFrame containing the data for analysis
:type data: pd.DataFrame
:param beg_date: The column name in the DataFrame that represents the start date of employment for
each employee. By default, it is set to "HireDate", defaults to HireDate (optional)
:param end_date: The `end_date` parameter is the name of the column in the `data` DataFrame that
represents the end date of the tenure period for each employee. This column should contain date
values in the format specified by the `date_format` parameter (default is "%Y-%m-%d"), defaults to
MetricDate (optional)
:param maxten: The `maxten` parameter is used to specify the maximum tenure in years. It is used to
identify employees with a tenure greater than or equal to the specified value, defaults to 40
(optional)
:param return_type: The `return_type` parameter determines the type of output that the function will
return. It can have the following values:, defaults to message (optional)
:param date_format: The `date_format` parameter is used to specify the format of the date strings in
the `beg_date` and `end_date` columns of the input data. It is used when converting these columns to
datetime format using the `pd.to_datetime` function. The default value is "%Y-%m, defaults to
%Y-%m-%d (optional)
:return: The function `identify_tenure` returns different outputs based on the value of the
`return_type` parameter. The possible return values are:
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def identify_tenure(data: pd.DataFrame,
                    beg_date = "HireDate",
                    end_date = "MetricDate",
                    maxten = 40,
                    return_type = "message", # use return_type to avoid conflict with built-in function
                    date_format = "%Y-%m-%d"): 
  required_variables = [beg_date, end_date]
  # check if required columns are not present
  check_inputs(data, requirements = required_variables)

  # Re-format and access columns by name, not by symbol
  data[end_date] = pd.to_datetime(data[end_date], format = date_format)
  data[beg_date] = pd.to_datetime(data[beg_date], format = date_format)

  # Sort by end_date and get the last date
  data_prep = data.sort_values(by = end_date)
  last_date = data_prep[end_date].iloc[-1]

  # graphing data
  tenure_summary = (data_prep[data_prep[end_date] == last_date]
                    .assign(tenure_years = lambda x: (x[end_date] - x[beg_date]).dt.days / 365)
                    .groupby("tenure_years")
                    .size()
                    .reset_index(name = "n"))

  # odd person IDs are the ones with tenure >= max tenure
  oddpeople = (data_prep[data_prep[end_date] == last_date]
               .assign(tenure_years = lambda x: (x[end_date] - x[beg_date]).dt.days / 365)
               .query(f"tenure_years >= {maxten}")
               .loc[:, "PersonId"])

  # message
  Message = (f"The mean tenure is {round(tenure_summary['tenure_years'].mean(), 1)} years.\n"
             f"The max tenure is {round(tenure_summary['tenure_years'].max(), 1)}.\n"
             f"There are {len(tenure_summary[tenure_summary['tenure_years'] >= maxten])} employees with a tenure greater than {maxten} years.")

  if return_type == "text":
    return Message

  elif return_type == "message":
    print(Message)

  elif return_type == "plot":
    # suppress warnings
    import warnings
    warnings.filterwarnings("ignore")

    density = gaussian_kde(tenure_summary["tenure_years"])
    
    # plot density
    plt.figure()
    plt.title("Tenure - Density")
    plt.xlabel("Tenure in Years")
    plt.ylabel("Density - number of employees")
    xs = np.linspace(0, maxten, data.shape[0])
    plt.plot(xs, density(xs), color = "#1d627e")
    plt.show()

  elif return_type == "data_cleaned":
    return data[~data["PersonId"].isin(oddpeople)]

  elif return_type == "data_dirty":
    return data[data["PersonId"].isin(oddpeople)]

  elif return_type == "data":
    return (data_prep[data_prep["Date"] == last_date]
            .assign(TenureYear = lambda x: (x[end_date] - x[beg_date]).dt.days / 365)
            .loc[:, ["PersonId", "TenureYear"]])

  else:
    raise ValueError("Error: please check inputs for `return`")

def check_inputs(data, requirements):
  # Check if the required variables are in the data
  # Raise an error if not
  for var in requirements:
    if var not in data.columns:
      raise ValueError(f"Error: {var} is not in the data")