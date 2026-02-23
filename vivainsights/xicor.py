# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Calculate the Chatterjee (xi) correlation coefficient for a given metric.
"""

__all__ = ['xicor']

import numpy as np
from scipy.stats import rankdata

def xicor(x, y, ties=True):
    """
    Calculate Chatterjee's rank correlation coefficient.

    A measure of association between two variables, useful for identifying
    monotonic relationships.

    Parameters
    ----------
    x : array-like
        Numeric array representing the independent variable.
    y : array-like
        Numeric array representing the dependent variable.
    ties : bool, optional
        Whether to handle ties in the data. Defaults to ``True``.

    Returns
    -------
    float
        Chatterjee's rank correlation coefficient.

    Raises
    ------
    ValueError
        If ``x`` and ``y`` have different lengths.

    Examples
    --------
    >>> X = [1, 2, 3, 4, 5]
    >>> Y = [2, 1, 4, 3, 5]
    >>> xicor(X, Y)
    """
    
    n = len(x)
    if n != len(y):
        raise ValueError("The length of x and y must be the same.")
    
    # Sort Y based on the order of X
    ordered_Y = np.array(y)[np.argsort(x)]
    
    # Get the ranks of Y after sorting by X
    r = rankdata(ordered_Y, method='max' if ties else 'ordinal')
    
    if ties:
        # Handling ties: Use maximum rank for tied values
        l = rankdata(ordered_Y, method='max')
        
        # Calculate Chatterjee's coefficient with ties
        return 1 - n * np.sum(np.abs(np.diff(r))) / (2 * np.sum(l * (n - l)))
    else:
        # No ties: Simplified formula for the Chatterjee coefficient
        return 1 - 3 * np.sum(np.abs(np.diff(r))) / (n**2 - 1)
