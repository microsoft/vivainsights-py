# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This module provides functionality to check a query to ensure that it is suitable for analysis.
Prints diagnostic data about the data query to the console, with information such as 
date range, number of employees, HR attributes identified, etc.
"""

import pandas as pd
from .extract_hr import extract_hr
from .extract_date_range import extract_date_range


def check_query(data: pd.DataFrame, return_type: str = "message"):
    """
    Check a query to ensure that it is suitable for analysis.
    
    Prints diagnostic data about the data query to the console, with information 
    such as date range, number of employees, HR attributes identified, etc.
    
    This can be used with any person-level query, such as the standard person query, 
    Ways of Working assessment query, and the hourly collaboration query. When run, 
    this prints diagnostic data to the console.
    
    Parameters
    ----------
    data : pandas.DataFrame
        A person-level query in the form of a pandas DataFrame. This includes:
        - Standard Person Query
        - Ways of Working Assessment Query  
        - Hourly Collaboration Query
        
        All person-level queries have a `PersonId` column and a `MetricDate` column.
    
    return_type : str, optional
        String specifying what to return. This must be one of the following strings:
        - "message" (default): prints message to console
        - "text": returns string containing the diagnostic message
        
    Returns
    -------
    str or None
        A different output is returned depending on the value passed to the `return_type` argument:
        - "message": prints message to console and returns None
        - "text": returns string containing the diagnostic message
    
    Raises
    ------
    ValueError
        If input is not a DataFrame or if required columns are missing.
        
    Examples
    --------
    >>> import vivainsights as vi
    >>> loaded_data = vi.load_pq_data()
    >>> vi.check_query(loaded_data)
    >>> 
    >>> # To get the message as text
    >>> message_text = vi.check_query(loaded_data, return_type="text")
    """
    
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Input is not a pandas DataFrame.")
    
    if "PersonId" not in data.columns:
        raise ValueError("There is no `PersonId` variable in the input.")
    
    if "MetricDate" not in data.columns:
        raise ValueError("There is no `MetricDate` variable in the input.")
    
    # Build the diagnostic message
    main_chunk = ""
    
    # Employee count
    employee_count = data['PersonId'].nunique()
    new_chunk = f"There are {employee_count} employees in this dataset."
    main_chunk = new_chunk
    
    # Date range
    try:
        date_range_text = extract_date_range(data, return_type="text")
        main_chunk = main_chunk + "\n\n" + date_range_text
    except Exception:
        # Fallback if extract_date_range fails
        if "Date" in data.columns:
            date_col = pd.to_datetime(data["Date"], format="%m/%d/%Y")
        elif "MetricDate" in data.columns:
            date_col = pd.to_datetime(data["MetricDate"], format="%Y-%m-%d")
        else:
            date_col = pd.to_datetime(data["MetricDate"])
        
        date_text = f"Date ranges from {date_col.min().strftime('%Y-%m-%d')} to {date_col.max().strftime('%Y-%m-%d')}."
        main_chunk = main_chunk + "\n\n" + date_text
    
    # HR Variables
    try:
        hr_attributes = extract_hr(data, max_unique=200, return_type="suggestion")
        # Filter out non-HR columns like PersonId and date columns
        if hr_attributes:
            hr_filtered = [attr for attr in hr_attributes if attr not in ['PersonId', 'MetricDate', 'Date']]
            if hr_filtered:
                hr_count = len(hr_filtered)
                new_chunk = f"There are {hr_count} (estimated) HR attributes in the data:"
                main_chunk = main_chunk + "\n\n" + new_chunk
                
                # Format HR attributes with backticks like in R version
                hr_formatted = [f"`{attr}`" for attr in hr_filtered]
                hr_list = ", ".join(hr_formatted)
                main_chunk = main_chunk + "\n" + hr_list
    except Exception:
        # Fallback HR attribute detection
        object_cols = data.select_dtypes(include=['object']).columns.tolist()
        # Remove PersonId and date columns from HR attributes
        hr_cols = [col for col in object_cols if col not in ['PersonId', 'MetricDate', 'Date']]
        if hr_cols:
            hr_count = len(hr_cols)
            new_chunk = f"There are {hr_count} (estimated) HR attributes in the data:"
            main_chunk = main_chunk + "\n\n" + new_chunk
            
            hr_formatted = [f"`{attr}`" for attr in hr_cols]
            hr_list = ", ".join(hr_formatted)
            main_chunk = main_chunk + "\n" + hr_list
    
    # IsActive flag
    if "IsActive" not in data.columns:
        new_chunk = "The `IsActive` flag is not present in the data."
        main_chunk = main_chunk + "\n\n" + new_chunk
    else:
        # Convert to boolean and count active employees
        data_copy = data.copy()
        data_copy['IsActive'] = data_copy['IsActive'].astype(bool)
        active_count = data_copy[data_copy['IsActive'] == True]['PersonId'].nunique()
        new_chunk = f"There are {active_count} active employees out of all in the dataset."
        main_chunk = main_chunk + "\n\n" + new_chunk
    
    # Return based on return_type
    if return_type == "message":
        print(main_chunk)
        return None
    elif return_type == "text":
        return main_chunk
    else:
        raise ValueError("Please check inputs for `return_type`. Must be 'message' or 'text'.")