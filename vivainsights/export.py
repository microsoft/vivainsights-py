# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Display and export data frames and plot objects to various formats.

Functions:
- display_plot: Universal function to display plots regardless of type (matplotlib.Figure or seaborn.FacetGrid)
- export: Exports data frames or plot objects using the specified method/format

By default, export() copies a data frame to the clipboard, and matplotlib objects are saved as PNG files.
"""

__all__ = ['display_plot', 'export']

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns

def display_plot(plot_obj):
    """
    Universal function to display plots regardless of type.
    
    Handles both matplotlib.figure.Figure objects (from create_bar, create_trend, etc.)
    and seaborn.axisgrid.FacetGrid objects (from create_line with >4 groups).
    
    Parameters
    ----------
    plot_obj : matplotlib.figure.Figure or seaborn.axisgrid.FacetGrid
        The plot object to display
        
    Returns
    -------
    None
        Displays the plot using the appropriate method
        
    Examples
    --------
    >>> import vivainsights as vi
    >>> plot = vi.create_line(data=vi.load_pq_data(), metric='Email_hours', hrvar='Organization')
    >>> vi.display_plot(plot)
    """
    if hasattr(plot_obj, 'show'):
        # For matplotlib Figure objects
        plot_obj.show()
    elif isinstance(plot_obj, sns.axisgrid.FacetGrid) or hasattr(plot_obj, 'figure'):
        # For seaborn FacetGrid objects - use matplotlib's show
        plt.show()
    else:
        # Fallback - just use plt.show()
        print(f"Unknown plot type: {type(plot_obj)}, using plt.show() as fallback")
        plt.show()

def export(x,
           file_format='auto',
           path='insights export',
           dpi=300,
           timestamp=True):
           
        """
        Export data frames or plot objects to various formats.

        A general-purpose function to export vivainsights outputs to CSV,
        clipboard, or save as images. By default, copies a DataFrame to the
        clipboard and displays plot objects.

        Parameters
        ----------
        x : pandas.DataFrame or matplotlib.figure.Figure
            Object to export.
        file_format : str, optional
            Export method. Defaults to ``"auto"`` which copies DataFrames to
            clipboard and displays plot objects. Other options:
            ``"csv"``, ``"png"``, ``"svg"``, ``"jpeg"``, ``"pdf"``,
            ``"clipboard"``, ``"display"``.
        path : str, optional
            File path (without extension). Defaults to ``"insights export"``.
        dpi : int, optional
            Dots per inch for image export. Defaults to 300.
        timestamp : bool, optional
            Whether to append a timestamp to the file name. Defaults to ``True``.

        Returns
        -------
        None
            Output is written to disk, clipboard, or displayed depending on
            ``file_format``.

        Examples
        --------
        >>> import vivainsights as vi
        >>> # Auto behavior — plot will be displayed
        >>> km_plot = vi.keymetrics_scan(data=vi.load_pq_data(), hrvar='Organization', return_type="plot")
        >>> vi.export(km_plot)
        >>>
        >>> # Auto behavior — DataFrame will be copied to clipboard
        >>> data = vi.load_pq_data()
        >>> vi.export(data)
        >>>
        >>> # Explicit file export
        >>> vi.export(km_plot, file_format='png', path='keymetrics_scan', timestamp=False)
        """
    
        # Determine object type for auto behavior
        is_plot = (isinstance(x, plt.Figure) or 
                  isinstance(x, sns.axisgrid.FacetGrid) or 
                  hasattr(x, 'savefig'))
        is_dataframe = isinstance(x, pd.DataFrame)
        
        # Handle auto file format
        if file_format == "auto":
            if is_plot:
                file_format = "display"
            elif is_dataframe:
                file_format = "clipboard"
            else:
                raise ValueError(f"Unknown object type: {type(x)}. Cannot determine auto behavior.")
        
        # Create timestamped path (if applicable)
        if timestamp == True:
            newpath = f"{path} {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
        else:
            newpath = path
            
        # Export option: CSV
        if file_format == "csv":
            if not is_dataframe:
                raise ValueError("CSV export is only supported for DataFrames.")
            newpath = f"{newpath}.csv"
            print(f"Exporting to {newpath}...")
            x.to_csv(newpath, index=False)

        # Export option: png,svg,jpeg,pdf
        elif file_format in ["png", "svg", "jpeg", "pdf"]:
            if not is_plot:
                raise ValueError(f"{file_format.upper()} export is only supported for plot objects.")
            newpath = f"{newpath}.{ file_format}"
            print(f"Exporting to {newpath}...")
            x.savefig( # matplotlib.savefig
                newpath,
                dpi = dpi, # Set dots per inch
                bbox_inches="tight", # Remove extra whitespace around plot
                facecolor='white' # Set background color to white   
                ) 

        # clipboard export
        elif file_format == "clipboard":
            if not is_dataframe:
                raise ValueError("Clipboard export is only supported for DataFrames.")          
            x.to_clipboard()                      
            print("Data frame copied to clipboard.\nYou may paste the contents directly to Excel.")
            
        # display plot
        elif file_format == "display":
            if not is_plot:
                raise ValueError("Display is only supported for plot objects.")
            display_plot(x)
            
        else:
            raise ValueError(f"Invalid file_format: {file_format}. Supported formats: 'auto', 'csv', 'png', 'svg', 'jpeg', 'pdf', 'clipboard', 'display'")        
        return()