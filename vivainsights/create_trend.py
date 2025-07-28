# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The `create_trend` function provides a week by week view of a selected Viva Insights metric, 
allowing you to either return a week by week heatmap bar plot or a summary table. 
By default, `create_trend` returns a week by week heatmap bar plot, highlighting the points intime with most activity. 
Additional options available to return a summary table.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from vivainsights.extract_date_range import extract_date_range
from vivainsights import totals_col

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
                 date_format: str = "%Y-%m-%d",
                 size_x_axis_label: int = 5
                 ):  
  """
  Name
  ----
  create_trend

  Description
  -----------
  This module provides a week by week view of a selected Viva Insights metric. 
  By default returns a week by week heatmap bar plot, highlighting the points intime with most activity. 
  Additional options available to return a summary table.
    
  Parameters
  ---------
  data : panda dataframe
      The input data as a pandas DataFrame.
  metric : str
    The metric parameter is a string that represents the column name in the data DataFrame that contains the values to be plotted or analyzed. This could be any numerical metric such as sales, revenue, or number of hours worked.
  palette : list
    The `palette` parameter is a list of colors that will be used to represent different groups in the trend plot. Each color in the list corresponds to a different group. By default, the palette includes 8 colors, but you can modify it to include more or fewer colors if needed.
  hrvar : str
    hrvar is a string parameter that represents the variable used for grouping the data. In this case, it is used to group the data by organization. Defaults to Organization mingroup: The `mingroup` parameter is used to specify the minimum number of groups that should be present in the data for the trend analysis. If the number of unique values in the `hrvar` column is less than `mingroup`, the function will raise an error. Defaults to 5
  return_type : str
      The `return_type` parameter determines the type of output that the function will return. It can have two possible values:. Defaults to plot
  legend_title : str
      The title for the legend in the plot. It is used to label the different categories or groups in the data. Defaults to Hours
  date_column : str
      The name of the column in the DataFrame that contains the dates for the trend analysis. Defaults to MetricDate
  date_format : str
      The `date_format` parameter is used to specify the format of the dates in the `date_column` of the input data. It should be a string that follows the syntax of the Python `datetime` module's `strftime` function. This allows you to specify how the dates are formatted in the. Defaults to %Y-%m-%d

  Returns
  ------
  The function `create_trend` returns either a table or a plot, depending on the value of the `return_type` parameter.

  Example
  -------
  >>> import vivainsights as vi
  >>> pq_data = vi.load_pq_data()  
  >>> create_trend(data = pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
  """
  
  if(hrvar is None):
        data = totals_col(data)
        hrvar = "Total"
        
  # Return the table or the plot or raise an error
  if return_type == "table":    
    myTable = create_trend_calc(data, metric, hrvar, mingroup, date_column, date_format)
    myTable_return = myTable.pivot(index="group", columns=date_column, values=metric)
    return myTable_return    
  elif return_type == "plot":
    return create_trend_viz(data, metric, palette, hrvar, mingroup, legend_title, date_column, date_format, size_x_axis_label)
  else:
    raise ValueError("Please enter a valid input for return_type.")
  
def create_trend_calc(data, metric, hrvar, mingroup, date_column, date_format):
  """
  Name 
  ----
  create_trend_calc

  Description
  -----------
  This function creates a trend calculation by grouping data by a specified variable and calculating
  the mean of a specified metric over time.
  """
  # Check inputs
  required_variables = [date_column, metric, "PersonId"]

  # Error message if variables are not present
  # Nothing happens if all present
  for var in required_variables:
    if var not in data.columns:
      raise ValueError(f"{var} is not in the data")


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
  date_format: str,
  size_x_axis_label
):
  """
  Name
  ----
  create_trend_viz

  Description
  -----------
  This function creates a heatmap visualization of trends in a given metric by a specified variable
  over time.
  """
  
  myTable = create_trend_calc(data, metric, hrvar, mingroup, date_column, date_format)
  myTable_plot = myTable[[date_column, "group", metric]]  
  
  # Cleaning labels for plotting
  clean_nm = metric.replace("_", " ")  
  title_text = f"{clean_nm} Hotspots"
  subtitle_text = f'By {hrvar}'
  caption_text = extract_date_range(data, return_type = 'text')  
  
  # Creating the plot object
  fig, ax = plt.subplots(figsize=(7, 4))
    
  # Removing tick marks
  ax.tick_params(
      which='both',      # Both major and minor ticks are affected
      top=False,         # Remove ticks from the top
      bottom=False,      # Remove ticks from the bottom
      left=False,        # Remove ticks from the left
      right=False        # Remove ticks from the right
  )
  
  # Creating Pivot the data and sort columns
  pivot_table = myTable_plot.pivot(index="group", columns=date_column, values=metric)
  pivot_table = pivot_table.sort_index(axis=1)

  # Creating heatmap
  sns.heatmap(
      data=pivot_table,
      cmap=palette,
      cbar_kws={"label": legend_title},
      xticklabels=False
  )

  # Calculating date range and generate tick labels
  date_range_days = (pivot_table.columns.max() - pivot_table.columns.min()).days
  date_list = list(pivot_table.columns)

  # Deciding format and deduplicate

  tick_labels = []
  last_label = ""
  for d in date_list:
      if date_range_days > 365:
          label = d.strftime('%Y')
      elif date_range_days > 90:
          label = d.strftime('%b %Y')
      else:
          label = d.strftime('%d-%m-%y')

      if label != last_label:
          tick_labels.append(label)
          last_label = label
      else:
          tick_labels.append("")  # Empty for duplicate to avoid clutter

  # Explicitly setting the x-ticks positions and labels
  ax.set_xticks([i + 0.5 for i in range(len(date_list))])  # heatmap cell centers
  ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=9)

  
  # Grouping indices by the bracket label
  bracket_groups = {}
  current_label = None
  for idx, label in enumerate(tick_labels):
      if label != "":
          current_label = label
          bracket_groups[current_label] = [idx, idx]
      else:
          if current_label:
              bracket_groups[current_label][1] = idx
  
  # Drawing brackets clearly under each grouped label
  bracket_y = -0.08
  for label, (start, end) in bracket_groups.items():
      ax.hlines(y=bracket_y, xmin=start, xmax=end + 1, color='black', linewidth=1.2, transform=ax.get_xaxis_transform(), clip_on=False)
      ax.vlines([start, end + 1], ymin=bracket_y - 0.01, ymax=bracket_y, color='black', linewidth=1.2, transform=ax.get_xaxis_transform(), clip_on=False)
      ax.text((start + end + 1) / 2, bracket_y - 0.03, label, ha='center', va='top', fontsize=size_x_axis_label, transform=ax.get_xaxis_transform(), clip_on=False)
  
  # Adding padding at bottom for brackets and labels
  plt.subplots_adjust(bottom=0.12)

  # Set x-tick labels
  # ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=9)


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
  ax.xaxis.set_major_locator(plt.NullLocator())
  ax.xaxis.set_major_formatter(plt.NullFormatter())

  # Set caption
  ax.text(x=-0.08, y=-0.12, s=caption_text, transform=fig.transFigure, ha='left', fontsize=9, alpha=.7)
  
  # return the plot object
  return fig