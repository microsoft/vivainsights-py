# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Detect holiday weeks by scanning for anomalous collaboration hours.

Returns a list of weeks that appear to be
holiday weeks and optionally an edited dataframe with outliers removed. By
default, missing values are excluded.
"""

__all__ = ['identify_holidayweeks']

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator


def identify_holidayweeks(data: pd.DataFrame, sd = 1, return_type = "text",figsize: tuple = None):
    """Detect holiday weeks by scanning for anomalous collaboration hours.

    Scans a standard person query for weeks where collaboration hours fall
    far below the mean.  As best practice, run this function before other
    analyses to remove atypical weeks from the dataset.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.  Must contain ``MetricDate`` and
        ``Collaboration_hours``.
    sd : int or float, default 1
        Number of standard deviations below the mean to flag as an
        outlier.  Enter a positive number.
    return_type : str, default "text"
        One of ``"text"``, ``"labelled_data"`` / ``"dirty_data"`` /
        ``"data_dirty"``, ``"cleaned_data"`` / ``"data_cleaned"``,
        ``"holidayweeks_data"``, or ``"plot"``.
    figsize : tuple or None, default None
        Figure size ``(width, height)`` in inches.  Defaults to ``(8, 6)``.

    Returns
    -------
    str, pandas.DataFrame, or matplotlib.figure.Figure
        A diagnostic string, a filtered dataset, or a line chart
        depending on *return_type*.

    Examples
    --------
    Return a text summary of detected holiday weeks:

    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.identify_holidayweeks(pq_data, sd=0.75, return_type="text")

    Return a line chart highlighting holiday weeks:

    >>> vi.identify_holidayweeks(pq_data, sd=0.75, return_type="plot")

    Return a cleaned dataset with holiday weeks removed:

    >>> vi.identify_holidayweeks(pq_data, sd=0.75, return_type="cleaned_data")

    Return the dataset with holiday weeks labelled:

    >>> vi.identify_holidayweeks(pq_data, sd=0.75, return_type="labelled_data")
    """

    try:
        # convert `MetricDate` to datetime
        data['MetricDate'] = pd.to_datetime(data.MetricDate)

        # Calculate the mean and z-score of collaboration hours by date
        Calc = data.dropna(subset=['MetricDate', 'Collaboration_hours']).groupby("MetricDate").agg(mean_collab = ("Collaboration_hours", "mean")).reset_index()
        Calc["z_score"] = (Calc["mean_collab"] - Calc["mean_collab"].mean())/ Calc["mean_collab"].std()


        # Find the outliers that are below the given standard deviation
        Outliers = (Calc["MetricDate"][Calc["z_score"] < -sd])

        Calc = Calc.assign(Outlier = Calc["MetricDate"].isin(Outliers))
        
        # Return the message or the plot depending on the argument
        if return_type== "text":
            # Calculate the total return_type and the message
            mean_collab_hrs = Calc["mean_collab"].mean()

            if len(Outliers) == 0:
                Message = 'There are no weeks where collaboration was ' + str(sd) + ' standard deviations below the mean (' + str(round(mean_collab_hrs, 1)) + ').'
            else:
                Message = 'The weeks where collaboration was ' + str(sd) + ' standard deviations below the mean (' + str(round(mean_collab_hrs, 1)) + ') are: '
                Message += ', '.join(Outliers.apply(lambda x: "`" + x.strftime("%m/%d/%Y") + "`"))
            
            return Message
        
        elif return_type in ["labelled_data", "dirty_data", "data_dirty"]:
            
            data_labelled = data.assign(holidayweek = data["MetricDate"].isin(Outliers))
            return data_labelled
        
        elif return_type in ["cleaned_data", "data_cleaned"]:
            data_cleaned = data[~data["MetricDate"].isin(Outliers)]
            
            if len(Outliers) == 0:
                print(f"No holiday weeks were removed. Standard deviation threshold was {sd}.")
            else:
                outlier_dates = ', '.join(Outliers.dt.strftime("%Y-%m-%d"))
                print(f"The weeks {outlier_dates} have been flagged as holiday weeks and removed from the data.")
                print(f"This is based on a standard deviation of {sd} below the mean collaboration hours.")
            
            return data_cleaned

        
        elif return_type == "holidayweeks_data":
            data_hw = data[data["MetricDate"].isin(Outliers)]
            return data_hw
        
        elif return_type == "plot":
            # Generate a line plot with matplotlib for the collaboration hours
            fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))

            # Plot the collaboration hours
            ax.plot(Calc["MetricDate"], Calc["mean_collab"].round(0), color="#1d627e", linewidth=3)

            # Add a marker to indicate the holiday weeks
            ax.scatter(Calc[Calc.Outlier==True]["MetricDate"], Calc[Calc.Outlier==True]["mean_collab"].round(0), color="#fe7f4f", marker="o", s=150, zorder=3)

            # Create the strings for the title, subtitle and caption
            subtitle_str = "Average collaboration hours where markers indicate holiday weeks"
            cap_str = "Data from week of {} to week of {}".format(Calc["MetricDate"].min().strftime("%b %d, '%y"), Calc["MetricDate"].max().strftime("%b %d, '%y"))

            # Set the title, subtitle, labels and limits of the plot
            ax.set_xlabel("Date", fontsize=12, fontweight="bold")
            ax.set_ylabel("Collaboration Hours", fontsize=12, fontweight="bold")
            ax.set_ylim(0, None)
            ax.text(x=ax.get_xlim()[0]-5, y=ax.get_ylim()[1]*1.10, s="Holiday Weeks", fontsize=16, fontweight="bold")
            ax.text(x=ax.get_xlim()[0]-5, y=ax.get_ylim()[1]*1.05, s=subtitle_str, fontsize=12)
            ax.text(x=ax.get_xlim()[0]-5,y=ax.get_ylim()[0]-5.5,s=cap_str, fontsize=12)
            
            ax.xaxis.set_major_locator(FixedLocator(range(len(Calc)))) # Set the tick positions
            ax.set_xticklabels(pd.to_datetime(Calc['MetricDate']).dt.strftime("%b %d, '%y"), rotation=45, ha="right")
            ax.grid(False)
            
            return fig
        else:
            raise ValueError("The `return_type` argument must be one of the following strings: 'text', 'labeled_data', 'cleaned_data', 'holidayweeks_data', or 'plot'.")
    except:

        # Check for the error in the input data
        required_cols = ['MetricDate', 'Collaboration_hours']
        for i in required_cols:
            if i not in data.columns:
                raise ValueError("The required variable {} is not present in the dataframe.".format(i))
                 
        if pd.api.types.is_datetime64_any_dtype(data['MetricDate'])==False:
            raise ValueError("`MetricDate` appears not to be properly formatted. It needs to be in the format YYYY-MM-DD. Also check for missing values or stray values with inconsistent formats.")
        
