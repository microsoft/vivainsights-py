# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module creates a data validation report that combines multiple validation checks
into a single HTML report.
"""

import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os

# Import validation functions from the package
from vivainsights.identify_holidayweeks import identify_holidayweeks
from vivainsights.identify_nkw import identify_nkw
from vivainsights.identify_outlier import identify_outlier
from vivainsights.hrvar_count import hrvar_count


def _generate_plot_base64(fig):
    """
    Convert a matplotlib figure to a base64 encoded string for embedding in HTML.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The matplotlib figure to convert
        
    Returns
    -------
    str
        Base64 encoded string with data URI prefix
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


def _style_dataframe_html(df):
    """
    Convert a pandas DataFrame to styled HTML table.
    
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to convert
        
    Returns
    -------
    str
        HTML string of the styled table
    """
    if df is None or df.empty:
        return ""
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Format numeric columns to 2 decimal places if they contain percentages
    for col in df_copy.columns:
        if 'perc' in col.lower() or 'percent' in col.lower():
            df_copy[col] = df_copy[col].apply(lambda x: f"{x*100:.1f}%" if pd.notnull(x) else "")
    
    return df_copy.to_html(index=False, border=0, classes='table')


def validation_report(
    data: pd.DataFrame,
    output_path: str = "validation_report.html",
    hrvar: list = None,
    return_type: str = "html"
):
    """
    Name
    ----
    validation_report
    
    Description
    -----------
    Generate a comprehensive data validation report that includes checks for:
    - Holiday weeks (identify_holidayweeks)
    - Non-knowledge workers (identify_nkw)
    - Outliers in collaboration metrics (identify_outlier)
    - HR attributes group sizes and missing values (hrvar_count)
    
    The function creates an HTML report with validation results, including
    text summaries, tables, and plots.
    
    Parameters
    ----------
    data : pd.DataFrame
        A Standard Person Query dataset in the form of a pandas DataFrame.
    output_path : str, optional
        Path where the HTML report will be saved. Defaults to "validation_report.html".
    hrvar : list, optional
        List of HR variables to analyze. If None, defaults to ['Organization', 'LevelDesignation'].
    return_type : str, optional
        Type of output to return. Options are:
        - 'html': Save and return the path to the HTML file (default)
        - 'print_only': Print the report to console without saving
        
    Returns
    -------
    str or None
        If return_type is 'html', returns the path to the generated HTML file.
        If return_type is 'print_only', prints validation results and returns None.
        
    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.validation_report(pq_data, output_path="data_validation.html")
    'data_validation.html'
    
    >>> vi.validation_report(pq_data, hrvar=['Organization', 'FunctionType'])
    'validation_report.html'
    """
    
    # Set default HR variables if not provided
    if hrvar is None:
        hrvar = ['Organization', 'LevelDesignation']
    
    # Ensure hrvar is a list
    if isinstance(hrvar, str):
        hrvar = [hrvar]
    
    # Calculate metadata about the dataset
    metadata = {
        'Total Records': len(data),
        'Unique Employees': data['PersonId'].nunique() if 'PersonId' in data.columns else 'N/A',
        'Date Range': f"{data['MetricDate'].min()} to {data['MetricDate'].max()}" if 'MetricDate' in data.columns else 'N/A',
        'Report Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # For print_only mode, just output text summaries
    if return_type == 'print_only':
        print("=" * 80)
        print("DATA VALIDATION REPORT")
        print("=" * 80)
        print("\nDataset Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        print("\n" + "-" * 80)
        print("HOLIDAY WEEKS IDENTIFICATION")
        print("-" * 80)
        hw_message = identify_holidayweeks(data, sd=1, return_type='text')
        print(hw_message)
        
        print("\n" + "-" * 80)
        print("NON-KNOWLEDGE WORKERS IDENTIFICATION")
        print("-" * 80)
        nkw_message = identify_nkw(data, collab_threshold=5, return_type='text')
        print(nkw_message)
        
        print("\n" + "-" * 80)
        print("HR ATTRIBUTES REVIEW")
        print("-" * 80)
        for hv in hrvar:
            if hv in data.columns:
                print(f"\n{hv}:")
                hv_table = hrvar_count(data, hrvar=hv, return_type='table')
                print(hv_table.to_string(index=False))
        
        print("\n" + "=" * 80)
        return None
    
    # Generate holiday weeks section
    holiday_weeks_section = {}
    try:
        hw_message = identify_holidayweeks(data, sd=1, return_type='text')
        holiday_weeks_section['message'] = hw_message
        
        # Determine message type based on content
        if '[Pass]' in hw_message or 'no weeks' in hw_message.lower():
            holiday_weeks_section['message_type'] = 'pass'
        elif '[Warning]' in hw_message or 'flagged' in hw_message.lower():
            holiday_weeks_section['message_type'] = 'warning'
        else:
            holiday_weeks_section['message_type'] = 'info'
        
        # Generate plot
        try:
            hw_fig = identify_holidayweeks(data, sd=1, return_type='plot')
            holiday_weeks_section['plot'] = _generate_plot_base64(hw_fig)
        except Exception as e:
            print(f"Warning: Could not generate holiday weeks plot: {e}")
            holiday_weeks_section['plot'] = None
    except Exception as e:
        print(f"Warning: Could not generate holiday weeks section: {e}")
        holiday_weeks_section = None
    
    # Generate non-knowledge workers section
    nkw_section = {}
    try:
        nkw_message = identify_nkw(data, collab_threshold=5, return_type='text')
        nkw_section['message'] = nkw_message
        
        # Determine message type
        if '[Pass]' in nkw_message:
            nkw_section['message_type'] = 'pass'
        elif '[Warning]' in nkw_message:
            nkw_section['message_type'] = 'warning'
        else:
            nkw_section['message_type'] = 'info'
        
        # Get summary table
        try:
            nkw_table = identify_nkw(data, collab_threshold=5, return_type='data_summary')
            if not nkw_table.empty:
                nkw_section['table'] = _style_dataframe_html(nkw_table)
            else:
                nkw_section['table'] = None
        except Exception as e:
            print(f"Warning: Could not generate NKW table: {e}")
            nkw_section['table'] = None
    except Exception as e:
        print(f"Warning: Could not generate NKW section: {e}")
        nkw_section = None
    
    # Generate outliers section
    outliers_section = {}
    try:
        outlier_table = identify_outlier(data, group_var='MetricDate', metric='Collaboration_hours')
        
        # Find extreme outliers (z-score < -2 or > 2)
        extreme_outliers = outlier_table[(outlier_table['zscore'] < -2) | (outlier_table['zscore'] > 2)]
        
        if len(extreme_outliers) > 0:
            outliers_section['message'] = f"Found {len(extreme_outliers)} dates with extreme collaboration outliers (z-score < -2 or > 2)."
            outliers_section['message_type'] = 'warning'
        else:
            outliers_section['message'] = "No extreme outliers detected in collaboration hours."
            outliers_section['message_type'] = 'pass'
        
        # Show top/bottom outliers
        display_table = pd.concat([
            outlier_table.nsmallest(5, 'zscore'),
            outlier_table.nlargest(5, 'zscore')
        ]).drop_duplicates().sort_values('zscore')
        
        outliers_section['table'] = _style_dataframe_html(display_table)
    except Exception as e:
        print(f"Warning: Could not generate outliers section: {e}")
        outliers_section = None
    
    # Generate HR variable sections
    hrvar_sections = []
    for hv in hrvar:
        if hv in data.columns:
            try:
                hv_table = hrvar_count(data, hrvar=hv, return_type='table')
                hrvar_sections.append({
                    'title': f'Group Sizes by {hv}',
                    'table': _style_dataframe_html(hv_table)
                })
            except Exception as e:
                print(f"Warning: Could not generate hrvar_count for {hv}: {e}")
    
    # Load template and generate HTML
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('validation_report_template.html')
    
    html_content = template.render(
        title='Data Validation Report',
        metadata=metadata,
        holiday_weeks_section=holiday_weeks_section,
        nkw_section=nkw_section,
        outliers_section=outliers_section,
        hrvar_sections=hrvar_sections,
        generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Validation report saved to: {output_path}")
    return output_path
