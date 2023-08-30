# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module accepts a data frame or matplotlib figure object and exports it using the specified method/format. 
By default, a data frame is copied to the clipboard, and matplotlib objects are saved as PNG files.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def export(x,
           file_format='clipboard',
           path='insights export',
           timestamp=True):
           
        """
        Name
        ----

        Description
        -----------
        Exports the data to the specified file format and saves it to the specified filename.
        A general use function to export 'vivainsights' outputs to CSV, clipboard, or save as
        images. By default, `export()` copies a data frame to the clipboard.
        
        Parameters
        ---------
        x : dataframe or matplotlib figure object
            The object to export, which can be a data frame or a matplotlib figure object.
        file_format : csv/png/svg/jpeg/pdf/clipboard 
            Character string specifying the method of export.
        path : str or optional 
            If exporting a file, enter the path and the desired file name. Defaults to "insights export". 
        timestamp : bool or optional 
            Logical vector specifying whether to include a timestamp in the file name. Defaults to True.
        
        Returns
        -------
        A different output is returned depending on the value passed to the `file_format`
        Argument:
        - `"clipboard"`: no return - data frame is saved to clipboard.
        - `"csv"`: CSV file containing data frame is saved to specified path.
        - `"png"`: PNG file containing '' object is saved to specified path.
        - `"svg"`: SVG file containing '' object is saved to specified path.
        - `"jpeg"`: JPEG file containing '' object is saved to specified path.
        - `"pdf"`: PDF file containing '' object is saved to specified path.

        """
    
        # Create timestamped path (if applicable)
        if timestamp == True:
            newpath = f"{path} {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
        else:
            newpath = path
            
        # Export option: CSV
        #TODO: Check if is data frame
        if file_format == "csv":
            newpath = f"{newpath}.csv"
            print(f"Exporting to {newpath}...")
            x.to_csv(newpath, index=False)

        # Export option: png,svg,jpeg,pdf
        #TODO: Check if this works for matplotlib figures
        elif file_format in ["png", "svg", "jpeg", "pdf"]:
            newpath = f"{newpath}.{ file_format}"
            print(f"Exporting to {newpath}...")
            x.savefig( # matplotlib.savefig
                newpath,
                dpi = 300, # Set dots per inch
                bbox_inches="tight", # Remove extra whitespace around plot
                facecolor='white' # Set background color to white   
                ) 

        # clipboard export
        #TODO: Check if is data frame
        elif file_format == "clipboard":          
            x.to_clipboard()                      
            print("Data frame copied to clipboard.\nYou may paste the contents directly to Excel.")
        else:
            raise ValueError("Please check inputs.")        
        return()