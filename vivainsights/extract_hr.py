# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module extracts HR attributes (organizational data) through a combination of detecting variable class, 
number of unique values, regular expressions. There is an option to return either just a list of the variable names 
or a DataFrame containing only the variables themselves.
"""
import pandas as pd
def extract_hr(
    data: pd.DataFrame,
    max_unique =50,
    exclude_constants =True,
    return_type: str = "names"):
    """    
    :param data: a pandas DataFrame containing the data to extract HR (highly-recurring) variables from
    :param max_unique: The maximum number of unique values a column can have to be included in the
    output, defaults to 50 (optional)
    :param exclude_constants: A boolean value (True/False) indicating whether to exclude columns with
    constant values or not. If True, columns with constant values will be excluded. If False, all
    columns will be included regardless of whether they have constant values or not, defaults to True
    (optional)
    :param return_type: The type of output to be returned, either "names" or "vars". If "names", the
    function will return the names of the columns that meet the specified criteria. If "vars", the
    function will return the actual columns that meet the specified criteria, defaults to names
    (optional)
    :return: The function is not returning anything. It is printing the column names of the object
    columns in the filtered dataframe.
    """
    try:
        if((isinstance(max_unique, int)) and (isinstance(exclude_constants, bool))\
        and (return_type.lower() == "names") or (return_type.lower() == "vars")):
            unqdf = data.loc[:,data.nunique()<=max_unique]

        if exclude_constants == False:
            unqdf = unqdf.loc[:,unqdf.nunique()!=1]
  
        elif not isinstance(max_unique, int):
            error ="Error! var max_unique should be an integer value. Please try again."

        elif not isinstance(exclude_constants, bool):
            error ="Error! var exclude_constants should be an boolean(True/False) value. Please try again."

        elif (return_type.lower() != "names") or (return_type.lower() != "vars"):
            error ="Error! var return_type should be either(names/vars) value. Please try again."

        if return_type == "vars":
            return unqdf.select_dtypes(['object'])
        #return print(*unqdf.columns+',\n')
        return print(*unqdf.select_dtypes(['object']).columns+',\n')
    
    except:
        print(error)