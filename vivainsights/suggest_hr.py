# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
""" 
Explanation
"""
import vivainsights as vi
def suggest_hr(data):
    """
    Name
    -----
    suggest_hr

    Description
    -----------
    Generates HR suggestions based on specified criteria.

    Parameters
    ----------
    data (pandas.DataFrame): Input HR data containing relevant columns.

    Returns
    ----------
    None: Prints suggested HR attributes.
    """
    # Something that represents organization (done, use the org hierarchy)
    # Up to three columns that represent function
    # Up to three columns that represent level
    # Up to three columns that represent geographic location
    # Something that represents remote/hybrid/onsite
    # Manager flag and Mgr+ flag (from hierarchy)
    # New hire flag (from HireDate)

    # Extract HR attributes (you can replace this with your actual extraction logic)
    extracted_hr = vi.extract_hr(data, return_type="suggestion")

    # Remove any unwanted columns (e.g., MetricDate)
    if "MetricDate" in extracted_hr:
        extracted_hr.remove("MetricDate")

    # Print unique values for each extracted HR attribute
    for each_hr in extracted_hr:
        print(f"{each_hr}: {data[each_hr].unique()}")