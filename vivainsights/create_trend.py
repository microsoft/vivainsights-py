# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from vivainsights.extract_date_range import extract_date_range

"""_summary_
This module provides a week by week view of a selected Viva Insights metric. 
By default returns a week by week heatmap bar plot, highlighting the points intime with most activity. 
Additional options available to return a summary table.
"""
def create_trend(data: pd.DataFrame,
                 metric: str,
                 palette = [
                    "#0c3c44",
                    "#1d627e",
                    "#34b1e2",
                    "#bfe5ee",
                    "#fcf0eb",
                    "#fbdacd",
                    "#facebc",
                    "#fe7f4f"
                    ],
                 hrvar: str = "Organization",
                 mingroup = 5,
                 return_type: str = "plot",
                 legend_title: str = "Hours",
                 date_column: str = "MetricDate",
                 date_format: str = "%Y-%m-%d"):  

  # Return the table or the plot or raise an error
  if return_type == "table":    
    myTable = create_trend_calc(data, metric, hrvar, mingroup, date_column, date_format)
    myTable_return = myTable.pivot(index="group", columns=date_column, values=metric)
    return myTable_return    
  elif return_type == "plot":
    return create_trend_viz(data, metric, palette, hrvar, mingroup, legend_title, date_column, date_format)
  else:
    raise ValueError("Please enter a valid input for return_type.")
  
def create_trend_calc(data, metric, hrvar, mingroup, date_column, date_format):
  """
  This function creates a trend calculation by grouping data by a specified variable and calculating
  the mean of a specified metric over time.
  
  :param data: The input data as a pandas DataFrame
  :param metric: The metric is a variable that represents the numerical value being analyzed in the
  data. It could be something like sales, revenue, or customer satisfaction score
  :param hrvar: hrvar is a variable that represents the time interval for grouping the data, such as
  "hour", "day", or "week". If hrvar is None, a dummy column called "Total" is created for grouping
  the data
  :param mingroup: mingroup is a parameter that specifies the minimum number of employees required in
  a group for it to be included in the trend calculation
  :param date_column: The name of the column in the input data that contains the date information
  :param date_format: The format of the date column in the data, e.g. "%Y-%m-%d" for "2022-01-01"
  :return: a pandas DataFrame containing the mean value of a given metric, the mean employee count,
  and the date and group columns. The DataFrame is filtered to only include groups with a minimum
  number of employees specified by the mingroup parameter.
  """
  # Check inputs
  required_variables = [date_column, metric, "PersonId"]

  # Error message if variables are not present
  # Nothing happens if all present
  for var in required_variables:
    if var not in data.columns:
      raise ValueError(f"{var} is not in the data")

  # Handling None values passed to hrvar
  if hrvar is None:
    data["Total"] = 1 # Create a dummy column for totals
    hrvar = "Total"

  # Clean metric name
  clean_nm = metric.replace("_", " ")

  # Convert Date to datetime and rename hrvar to group
  data[date_column] = pd.to_datetime(data[date_column], format=date_format)
  data = data.rename(columns={hrvar: "group"})

  # Select relevant columns and group by group
  myTable = data[["PersonId", date_column, "group", metric]]
  myTable = myTable.groupby("group")

  # Calculate employee count and filter by mingroup
  myTable = myTable.apply(lambda x: x.assign(Employee_Count = x["PersonId"].nunique()))
  myTable = myTable[myTable["Employee_Count"] >= mingroup]

  # Group by date and group and calculate mean metric and employee count
  myTable.reset_index(drop = True, inplace = True)
  myTable = myTable.groupby([date_column, "group"]).agg({"Employee_Count": "mean", metric: "mean"}).reset_index()

  return myTable
  
  
def create_trend_viz(
  data: pd.DataFrame,
  metric: str,
  palette,
  hrvar: str,
  mingroup,
  legend_title: str,
  date_column: str,
  date_format: str
):
  """
  This function creates a heatmap visualization of trends in a given metric by a specified variable
  over time.
  
  :param data: a pandas DataFrame containing the data to be visualized
  :type data: pd.DataFrame
  :param metric: The metric to be plotted on the y-axis of the heatmap
  :type metric: str
  :param palette: The color palette to use for the heatmap
  :param hrvar: hrvar stands for "high-level reference variable" and refers to the variable that is
  used to group the data in the visualization. For example, if the data is about sales by region,
  hrvar could be "region" and the visualization would show the trend of sales for each region over
  time
  :type hrvar: str
  :param mingroup: mingroup is a parameter that specifies the minimum number of observations required
  for a group to be included in the visualization
  :param legend_title: The title for the colorbar legend in the heatmap plot
  :type legend_title: str
  :param date_column: The name of the column in the input data that contains the date information
  :type date_column: str
  :param date_format: The format of the date column in the input data
  :type date_format: str
  """
  
  myTable = create_trend_calc(data, metric, hrvar, mingroup, date_column, date_format)
  myTable_plot = myTable[[date_column, "group", metric]]  
  # myTable_plot[date_column] = pd.to_datetime(myTable[date_column], format=date_format)
  # myTable_plot[date_column] = pd.to_datetime(myTable[date_column], format=date_format).dt.date
  
  # Clean labels for plotting
  clean_nm = metric.replace("_", " ")  
  title_text = f"{clean_nm}\nHotspots by {hrvar.lower()}"
  subtitle_text = f'By {hrvar}'
  caption_text = extract_date_range(data, return_type = 'text')  
  
  # Create the plot object
  # Setup plot size.
  fig, ax = plt.subplots(figsize=(7, 4))
    
  # Remove tick marks
  ax.tick_params(
      which='both',      # Both major and minor ticks are affected
      top=False,         # Remove ticks from the top
      bottom=False,      # Remove ticks from the bottom
      left=False,        # Remove ticks from the left
      right=False        # Remove ticks from the right
  )
  
  # Create heatmap plot
  sns.heatmap(
    data = myTable_plot.pivot(index="group", columns=date_column, values=metric),
    cmap = palette,
    cbar_kws={"label": legend_title},
    xticklabels= myTable_plot[date_column].dt.date.unique()
    )
  
  # Reformat x-axis tick labels
  ax.xaxis.set_tick_params(labelsize = 9, rotation=45)
  ax.yaxis.set_tick_params(labelsize = 9)
  # ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %y'))
  
  # Remove axis labels
  ax.set_xlabel('')
  ax.set_ylabel('')
  
  ax.plot(
    [-0.08, .9], # Set width of line, previously [-0.08, .9]
    [0.9, 0.9], # Set height of line
    transform = fig.transFigure, # Set location relative to plot
    clip_on = False,
    color = '#fe7f4f',
    linewidth = .6
)

  ax.add_patch(
      plt.Rectangle(
          (-0.08, 0.9), # Set location of rectangle by lower left corner, previously [-0.08, .9]
          0.05, # Width of rectangle
          -0.025, # Height of rectangle
          facecolor = '#fe7f4f',
          transform = fig.transFigure,
          clip_on = False,
          linewidth = 0
          )
  )        

  # Set title
  ax.text(
      x = -0.08, y = 1.00,
      s = title_text,
      transform = fig.transFigure,
      ha = 'left',
      fontsize = 13,
      weight = 'bold',
      alpha = .8
  )

  # Set subtitle
  ax.text(
      x = -0.08, y = 0.95,
      s = subtitle_text,
      transform = fig.transFigure,
      ha = 'left',
      fontsize = 11,        
      alpha = .8
  )

  # Set caption
  ax.text(x=-0.08, y=-0.12, s=caption_text, transform=fig.transFigure, ha='left', fontsize=9, alpha=.7)
  
  # return the plot object
  return fig
  
  """Legacy 
  # plot_object.set_title(f"{clean_nm}\nHotspots by {hrvar.lower()}")
  # plot_object.set_xlabel(date_column)
  # plot_object.set_ylabel(hrvar)
  """