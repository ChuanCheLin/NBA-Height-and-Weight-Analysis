import pandas as pd


def split_player_season(df):
    """Splits 'Player_Season' into 'Player' and 'Season'."""
    split_df = df['Unnamed: 0'].str.rsplit('_', n=1, expand=True)
    df['Player'] = split_df[0]
    df['Season'] = split_df[1].astype(str)
    return df.drop(columns=['Unnamed: 0'])


def calculate_averages(baseline_df, target_df):
    """Calculates before and after averages based on target seasons."""
    # Initialize dictionaries to store before and after averages
    before_averages = {}
    after_averages = {}

    # Iterate through each player in the target dataset
    for index, row in target_df.iterrows():
        player = row['Player']
        target_season = int(row['Season'].split('-')[0])  # Assuming format 'YYYY-YY'

        # Filter baseline data for this player
        player_data = baseline_df[baseline_df['Player'] == player]

        # Split the data into before and after target season
        before_data = player_data[player_data['Season'].apply(lambda x: int(x.split('-')[0]) in [target_season - 2, target_season - 1])]
        after_data = player_data[player_data['Season'].apply(lambda x: int(x.split('-')[0]) in [target_season + 1, target_season + 2])]

        # Calculate averages
        before_averages[player] = before_data[['PTS', 'AST', 'REB', 'FG_PCT']].mean()
        after_averages[player] = after_data[['PTS', 'AST', 'REB', 'FG_PCT']].mean()

    # Convert dictionaries to DataFrames
    before_averages_df = pd.DataFrame.from_dict(before_averages, orient='index')
    after_averages_df = pd.DataFrame.from_dict(after_averages, orient='index')

    return before_averages_df, after_averages_df


# Example usage
if __name__ == "__main__":
    # Load the datasets
    baseline_path = './OriginalDatasets/baseline_average_player_stats.csv'
    target_path = './OriginalDatasets/target_average_player_stats.csv'

    # Read the files
    base_df = pd.read_csv(baseline_path)
    tgt_df = pd.read_csv(target_path)

    # Split 'Player_Season' into 'Player' and 'Season' for both datasets
    base_df = split_player_season(base_df)
    tgt_df = split_player_season(tgt_df)

    # Calculate averages
    before_df, after_df = calculate_averages(base_df, tgt_df)

    # Displaying the first few rows of the resulting dataframes (optional)
    print(before_df.head())
    print(after_df.head())

    # Optional: Save the result to new CSV files
    before_df.to_csv('./OriginalDatasets/before_averages.csv')
    after_df.to_csv('./OriginalDatasets/after_averages.csv')
