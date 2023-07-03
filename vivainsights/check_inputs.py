# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
'''
The function `check_inputs` checks if the required variables are present in the given data and raises an error if any of them are missing.
'''
import pandas as pd

def check_inputs(data: pd.DataFrame, requirements: str):
  """
  Args:
    data (df): The `data` parameter is expected to be a pandas DataFrame object that contains the data to be checked.
    requirements (str): The `requirements` parameter is a list of variables that are required to be present in the `data` object. 
    
  The function `check_inputs` checks if each variable in the `requirements` list is present as a column in the `data` object. If any variable is missing, it raises an error.
  """
  # Check if the required variables are in the data
  # Raise an error if not
  for var in requirements:
    if var not in data.columns:
      raise ValueError(f"Error: {var} is not in the data")