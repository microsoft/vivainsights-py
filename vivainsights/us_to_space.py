# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Replace underscores with spaces in a given string.
"""

__all__ = ['us_to_space']

def us_to_space(string):
    """Replace underscores with spaces in a string.

    Parameters
    ----------
    string : str
        Input string potentially containing underscores.

    Returns
    -------
    str
        String with underscores replaced by spaces.

    Examples
    --------
    >>> from vivainsights import us_to_space
    >>> us_to_space("Meeting_and_call_hours_with_manager_1_1")
    'Meeting and call hours with manager 1 1'
    """
    return string.replace("_", " ")