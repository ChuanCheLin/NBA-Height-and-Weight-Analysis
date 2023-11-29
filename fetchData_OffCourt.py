# #### Import libraries

from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time


def fetch_and_process_player_data(player_id: int, season: str, target_stats: [str]):
    """
    Fetches and processes player game log data for a specific season.

    Parameters
    ----------
    player_id : int
        The ID of the player.
    season : str
        The season to fetch data for.
    target_stats : list of str
        The list of statistics to calculate averages for.

    Returns
    -------
    dict or str
        A dictionary with average stats if data is valid and available,
        otherwise a string message indicating the issue.
    """
    # Fetch player game log
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = game_log.get_data_frames()[0]

    # Data validation checks
    if df.empty:
        return f"No data available for player ID {player_id} in the {season} season."

    if df[target_stats].isnull().values.any():
        return f"Missing data for player ID {player_id} in the {season} season."

    if not all([pd.api.types.is_numeric_dtype(df[col]) for col in target_stats]):
        return f"Incorrect data types for player ID {player_id} in the {season} season."

    # Calculate average stats
    avg_stats = {stat: df[stat].mean() for stat in target_stats}

    return avg_stats


def fetch_data(
        fetch_players_seasons: dict,
        target_stats: list,
        request_delay=0.1,
):
    """
    Fetch average statistics for a given set of players over specified seasons.

    This function queries the NBA API to retrieve game logs for each player in each of their specified seasons.
    It then calculates the average statistics for the target metrics.

    Parameters
    ----------
    fetch_players_seasons : dict
        A dictionary where keys are player full names and values are lists of seasons to fetch data for.
        For example: {'LeBron James': ['2019', '2020'], 'Kevin Durant': ['2021']}

    target_stats : list of str
        The list of statistics to calculate averages for.

    request_delay : float, optional
        The delay (in seconds) between successive API requests to avoid overloading the server.
        Default is 0.1 seconds.

    Returns ------- dict A dictionary with player names as keys and another dictionary with average stats as values.
    For example: {'LeBron James': {'PPG': 25.34328358208955, 'APG': 10.208955223880597, 'RPG': 7.835820895522388,
    'FG%': 0.4896119402985075}, ...}

    Examples
    --------
    >>> fetch_players_seasons_test = {'LeBron James': ['2019']}
    >>> target_stats_test = ['PTS', 'AST', 'REB', 'FG_PCT']
    >>> fetch_data(fetch_players_seasons_test, target_stats_test)
    {'LeBron James_2019': {'PTS': 25.34328358208955, 'AST': 10.208955223880597, 'REB': 7.835820895522388, 'FG_PCT': 0.4896119402985075}}

    >>> fetch_players_seasons_test = {'Kobe Bryant': ['2019']}
    >>> fetch_data(fetch_players_seasons_test, target_stats_test)
    No data available for player ID 977 in the 2019 season.
    {}

    >>> fetch_players_seasons_test = {'LeBron James': ['2028']}
    >>> fetch_data(fetch_players_seasons_test, target_stats_test)
    No data available for player ID 2544 in the 2028 season.
    {}
    """

    average_stats = {}

    for name, seasons in fetch_players_seasons.items():
        player_dict = players.find_players_by_full_name(name)
        if player_dict:
            player_id = player_dict[0]["id"]
            for season in seasons:
                # Delay each API request
                time.sleep(request_delay)

                result = fetch_and_process_player_data(player_id, season, target_stats)
                if isinstance(result, dict):
                    average_stats[f'{name}_{season}'] = result
                else:
                    print(result)
                    continue

    return average_stats
