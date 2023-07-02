# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def check_inputs(data, requirements):
  # Check if the required variables are in the data
  # Raise an error if not
  for var in requirements:
    if var not in data.columns:
      raise ValueError(f"Error: {var} is not in the data")