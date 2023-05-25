# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
from datetime import datetime

def export(data,
           file_format='clipboard',
           path='insights export',
           timestamp=True,
           width=12,
           height=9):
           
        """
        Exports the data to the specified file format and saves it to the specified filename.
        A general use function to export 'vivainsights' outputs to CSV, clipboard, or save as
        images. By default, `export()` copies a data frame to the clipboard.
        
        Args:
            data (dataframe): The dataframe to export.
            file_format (csv/png/svg/jpeg/pdf/clipboard): Character string specifying the method of export.
            path (str, optional): If exporting a file, enter the path and the desired file name. Defaults to "insights export".
            timestamp (bool, optional): Logical vector specifying whether to include a timestamp in the file name. Defaults to True.
            width (int, optional): Width of the plot. Defaults to 12.
            height (int, optional): Height of the plot. Defaults to 9.
        Return: A different output is returned depending on the value passed to the `file_format`
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
            newpath =  path
        # Export option: CSV
        if  file_format == "csv":
            newpath = f"{newpath}.csv"
            data.to_csv(newpath, index=False)

        # Export option: png,svg,jpeg,pdf        
        elif  file_format in ["png", "svg", "jpeg", "pdf"]:
            newpath = f"{newpath}.{ file_format}"
            data.save(newpath, width= width, height= height)

        # clipboard export
        elif  file_format == "clipboard":          
            data.to_clipboard()                      
            print("Data frame copied to clipboard.\nYou may paste the contents directly to Excel.")
        else:
            raise ValueError("Please check inputs.")        
        return()