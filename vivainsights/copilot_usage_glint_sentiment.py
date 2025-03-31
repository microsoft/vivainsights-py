# Copilot X Glint Sentiment Relationship Strength
#This code analyzes employee engagement data, focusing on "Copilot Usage" metrics. 
#The code performs the following tasks:
    #1. Imports and cleans data from a CSV file that includes both Glint Score and Copilot Usage by user (Viva Insights Export).
    #2. Converts engagement scores to a 100-point scale and categorizes them into favorability groups (droping NEU responses).
    #3. Calculates weekly Copilot usage for employees.
    #4. Categorizes employees into user groups (e.g., PowerUser, NoviceUser) based on their Copilot activity.
    #5. Analyzes the relationship between Copilot usage categories and engagement scores using odds ratios.
    #6. Outputs insights on the strongest relationships between user categories and engagement metrics.








####### Install Libraries and initialization #######
# pip install --user pandas
#pip install --user scipy
def copilot_usage_glint_sentiment(file_name, survey_close_date, item_options = 5):
# INPUTS: 
# file_name: Path to the CSV file containing the data.
# item_options: Number of options in the survey (default is 5 for a 5-point scale).
# survey_close_date: The date when the survey closed (format: YYYY-MM-DD).

    import chardet
    import re
    from scipy.stats import percentileofscore
    import datetime
    import pandas as pd



    ######## IMPORT DATA  ########
    # The code will consider any data with "Copilot" in the column name as copilot activities.

    # EXPECTED DATA STRUCTURE
    ## | EMPLOYEE IDENTIFIER | GLINT ITEM | GLINT ITEM SCORE | COPILOT ITEMS ... | DATE OF COPILOT WEEKLY USAGE | 

    # SINGLE DATA SOURCE
    # SENSE DATA ENCODING
    with open(file_name, "rb") as f:
        result = chardet.detect(f.read())
        print(f"Detected Encoding: {result['encoding']}")
    # Load the Excel file into a pandas DataFrame
    df_glint = pd.read_csv(file_name , encoding=result['encoding'])





    ####### CLEAN DATA  ########
    
    # (Convert to favorability and drop neutral responses)

    # CONVERT TO 100PT SCALE FOR EASY FAVORABILITY PARSING
    df_glint['score100'] = (df_glint['Score'] - 1) * (100/(item_options-1))

    # CONVERT TO FAVORABILITY
    df_glint['favorability'] = df_glint['score100'].apply(lambda x: 'fav' if x > 70 else ('unfav' if x < 40 else 'neu'))

    # DROP NEUTRAL FAVORABILITY
    df_glint = df_glint[df_glint['favorability'] != 'neu']







    ###### ANALYZE DATA #########

    #Calculate "Copilot Usage" based on 12 week habit building literature and Odds Ratio methods comparing differing user types



    # CALCULATE COPILOT USAGE
    columns_to_include = ['Employee_ID', 'MetricDate']
    copilot_columns = df_glint.filter(regex='(?i)copilot', axis=1).columns

    # Select employee_id, date, and copilot-related columns
    df_glintscore_copilot = df_glint[columns_to_include + copilot_columns.tolist()].drop_duplicates()
    df_glintscore_copilot['MetricDate'] = pd.to_datetime(df_glintscore_copilot['MetricDate'], format='%m/%d/%Y', errors='coerce')

    # Define the start date for the past 12 weeks based on the survey close date
    start_date = survey_close_date - datetime.timedelta(weeks=12)

    # Filter data for the past 12 weeks
    df_past_12_weeks = df_glintscore_copilot[
        (df_glintscore_copilot['MetricDate'] >= start_date) & 
        (df_glintscore_copilot['MetricDate'] < survey_close_date)
    ]

    # COUNT ALL NON-ZERO COPILOT ACTIVITIES FOR EACH EMPLOYEE_ID AND DATE
    df_past_12_weeks['NonZero_Copilot_Activities'] = df_past_12_weeks.iloc[:, 2:].apply(lambda row: (row > 0).sum(), axis=1)

    # Group by Employee_ID and calculate weekly usage
    weekly_usage = df_past_12_weeks.groupby('Employee_ID')['NonZero_Copilot_Activities'].agg(
        total_usage='sum',
        avg_usage='mean'
    ).reset_index()


    # JOIN IN df_past_12_weeks_usage NonZero_Copilot_Activities FOR EACH USER TO weekly_usage SO WE HAVE HABIT BUILDING
    weekly_usage = weekly_usage.merge(df_past_12_weeks[['Employee_ID', 'NonZero_Copilot_Activities']].drop_duplicates(), on='Employee_ID', how='left')

    # Assign user categories
    # Power User: averaging 15+ weekly total Copilot actions and any use of Copilot in at least 9 out of past 12 weeks.
    # Habitual User: any use of Copilot in at least 9 out of past 12 weeks.
    # Novice User: averaging at least one Copilot action over the last 12 weeks.
    # Low User: having any Copilot action in the past 12 weeks.
    # Non-user: zero Copilot actions in the last 12 weeks.
    def assign_user_category(row):
        if row['total_usage'] > 0:
            if row['NonZero_Copilot_Activities'] >= 9:
                if row['avg_usage'] >= 15:
                    return 'PowerUser'
                else:
                    return 'HabitualUser'
        
            elif row['total_usage'] > 1:
                return 'NoviceUser'
            
            elif row['total_usage'] == 1:
                return 'LowUser'

            else:
                return 'NonUser'
        
        return 

    weekly_usage['UserCategory'] = weekly_usage.apply(assign_user_category, axis=1)

    # CATEGORIZE POWER-HABITUAL-NOVICE-LOW-NON
    weekly_usage['UserCategory_Group'] = weekly_usage['UserCategory'].apply(lambda x: 'HIGH' if x in('PowerUser', 'HabitualUser') else ('MED' if x in('NoviceUser','LowUser')  else 'NonUser')))

    # Merge the user categories back into the original DataFrame
    df_past_12_weeks_usage = df_past_12_weeks.merge(
        weekly_usage[['Employee_ID', 'UserCategory_Group']],
        on='Employee_ID',
        how='left'
    )

    # MERGE USERCATEGORY BACK INTO GLINT DATA
    df_glint_usage = df_glint.merge(
        df_past_12_weeks_usage[['Employee_ID', 'UserCategory_Group']],
        on='Employee_ID',
        how='left'
    ) [['Employee_ID', 'Glint_Item', 'Score', 'UserCategory_Group']]


    # OUTPUT THE COUNT OF EACH USER CATEGORY AND PERCENT OF TOTAL FORMATTED IN A TABLE
    user_category_counts = weekly_usage['UserCategory_Group'].value_counts()
    user_category_percent = user_category_counts / user_category_counts.sum() * 100
    user_category_table = pd.concat([user_category_counts, user_category_percent], axis=1)
    user_category_table.columns = ['Count', 'Percent']
    user_category_table = user_category_table.round(2)
    print(user_category_table)






    ###### Convert to Favorability and begin the Odds Ratio calculation #####

    # ADD FAVORABILITY COLUMN
    df_glint_usage['favorability'] = df_glint_usage['Score'].apply(lambda x: 'fav' if x >= 4 else ('unfav' if x <= 2 else 'neu'))
    df_glint_usage = df_glint_usage[df_glint_usage['favorability'] != 'neu']

    # GET COUNTS FOR EACH USER CATEGORY GROUPED BY GLINT ITEM AND FAVORABILITY
    df_glint_usage_grouped = df_glint_usage.groupby(['Glint_Item', 'favorability', 'UserCategory_Group'])['Employee_ID'].nunique().reset_index(name='user_count')

    # ADD 0.5 TO EACH COUNT TO AVOID DIVISION BY ZERO AND INF ODDS
    df_glint_usage_grouped['user_count'] = df_glint_usage_grouped['user_count'] + 0.5

    # PIVOT THE DATAFRAME TO GET FAV / UNFAV IN COLUMNS
    df_glint_usage_grouped_pivot = df_glint_usage_grouped.pivot_table(index=['Glint_Item', 'UserCategory_Group'], columns='favorability', values='user_count').reset_index()

    # DIVIDE FAV BY UNFAV TO GET ODDS
    df_glint_usage_grouped_pivot['odds'] = df_glint_usage_grouped_pivot['fav'] / df_glint_usage_grouped_pivot['unfav']

    # DROP NAN ODDS, THEN ADD "MAX" OR "MIN" LABEL TO THE THE MAX-MIN ODDS FOR EACH GLINT ITEM
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot.dropna(subset=['odds'])

    # DROP FAV AND UNFAV COLUMN AND PIVOT OUT USERCATEGORY_GROUP VALUES INTO NEW COLUMNS
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.drop(columns=['fav', 'unfav'])
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.pivot(index='Glint_Item', columns='UserCategory_Group', values='odds').reset_index()






    ###### Calculate and display final odds ratio #######

    # DROP NAN ODDS, THEN ADD "MAX" OR "MIN" LABEL TO THE THE MAX-MIN ODDS FOR EACH GLINT ITEM
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot.dropna(subset=['odds'])

    # DROP FAV AND UNFAV COLUMNS 
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.drop(columns=['fav', 'unfav'])

    # Identify the MAX and MIN odds for each Glint_Item and UserCategory_Group
    df_glint_usage_grouped_pivot_odds['MAX_MIN'] = df_glint_usage_grouped_pivot_odds.groupby('Glint_Item')['odds'].transform(
        lambda x: ['MAX' if val == x.max() else 'MIN' if val == x.min() else None for val in x])
    
    # DROP NONE VALUES FROM MAX_MIN COLUMN
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.dropna(subset=['MAX_MIN'])

    # PREPARE df_max_min FOR LATER JOIN
    df_max_min = df_glint_usage_grouped_pivot_odds[['Glint_Item', 'UserCategory_Group','MAX_MIN']]

    # DROP USERCATEGORY_GROUP COLUMN AND PIVOT MAX_MIN INTO COLUMNS
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.drop(columns='UserCategory_Group').drop_duplicates()
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.pivot(index='Glint_Item', columns='MAX_MIN', values='odds').reset_index()

    # TRY TO DIVIDE THE MAX ODDS BY THE MIN ODDS FOR EACH GLINT ITEM. IF THERE IS NO MIN COLUMN, PRINT ('NOT ENOUGH DATA')
    try:
        df_glint_usage_grouped_pivot_odds['odds_ratio'] = df_glint_usage_grouped_pivot_odds['MAX'] / df_glint_usage_grouped_pivot_odds['MIN']
    except KeyError:
        print('NOT ENOUGH DATA')
        df_glint_usage_grouped_pivot_odds['odds_ratio'] = None

    # DROP ANY ROW FROM df_glint_usage_grouped_pivot_odds THAT HAS A NAN VALUE
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.dropna()

    # JOIN df_glint_usage_grouped_pivot_odds WITH df_max_min TO GET THE USERCATEGORY_GROUP FOR THE MAX ODDS
    df_glint_usage_grouped_pivot_odds = df_glint_usage_grouped_pivot_odds.merge(df_max_min, on='Glint_Item', how='left')

    # Group by 'Glint_Item' and 'odds_ratio', then concatenate 'UserCategory_Group' values into a single string
    df_glint_usage_grouped_pivot_odds_final = df_glint_usage_grouped_pivot_odds.groupby(['Glint_Item', 'odds_ratio']).agg({
        'UserCategory_Group': lambda x: '-'.join(x).replace(' ', '')
    }).reset_index()





    # PRINT FINAL ODDS RATIO TABLE SORTED BY ODDS RATIO
    df_glint_usage_grouped_pivot_odds_final = df_glint_usage_grouped_pivot_odds_final.sort_values('odds_ratio', ascending=False).reset_index(drop=True)
    return df_glint_usage_grouped_pivot_odds_final



# Example usage of the function
import chardet
import re
from scipy.stats import percentileofscore
import datetime
import pandas as pd


survey_close_date = datetime.datetime.strptime('2024-09-29', '%Y-%m-%d')
file_name = 'C:/Users/bentankus/OneDrive - Microsoft/Projects/Copilot Support/glint_demodata_singlesource.csv'
copilot_usage = copilot_usage_glint_sentiment(file_name, survey_close_date, 5)

# NEW LINE FOR READABILITY
print('')

print(copilot_usage)