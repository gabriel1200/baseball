from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
import os

app = Flask(__name__)

# Load the MLB data
def load_data():
    data_file = os.path.join(os.path.dirname(__file__), 'data', 'mlb_full.csv')
    try:
        df = pd.read_csv(data_file)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# Global variable to store the data
MLB_DATA = load_data()
PLAYER_SUMMARY_DATA = pd.read_csv('data/mlb_player_averages.csv')
# Define which stats are better when lower
LEAGUE_AVERAGE=pd.read_csv('data/mlb_rate_stat_averages.csv')


@app.route('/')
def index():
    """Render the home page with player selection dropdown"""
    # Get unique players
    if not MLB_DATA.empty:
        players = MLB_DATA[['playerId', 'playerFullName']].drop_duplicates().sort_values('playerFullName')
        players_list = players.to_dict('records')
    else:
        players_list = []
    
    return render_template('index.html', players=players_list)

@app.route('/player/<int:player_id>')
def player_stats(player_id):
    """Render the player statistics page, including summary stats and rankings"""
    if MLB_DATA.empty or PLAYER_SUMMARY_DATA.empty:
        return render_template('player_stats.html', error="Data not available")
    
    # Filter data for the selected player
    player_data = MLB_DATA[MLB_DATA['playerId'] == player_id]
    player_summary = PLAYER_SUMMARY_DATA[PLAYER_SUMMARY_DATA['playerId'] == player_id]
    team_images=player_data['teamImage'].unique().tolist()

    if player_data.empty or player_summary.empty:
        return render_template('player_stats.html', error="Player not found")

    summary_row = player_summary.iloc[0]
    LOWER_IS_BETTER = {'K', 'HBP'} 

    # Helper to get rank for a single stat
    def get_rank(col):
        if col not in PLAYER_SUMMARY_DATA.columns:
            return None
        series = PLAYER_SUMMARY_DATA[col]
        if series.isnull().all():
            return None
        ascending = col in LOWER_IS_BETTER
        return int(series.rank(ascending=ascending, method='min')[PLAYER_SUMMARY_DATA['playerId'] == player_id].iloc[0])

    # Build unified player_info with summary stats
    player_info = {
        'id': player_id,
        'name': player_data['playerFullName'].iloc[0],
        'position': player_data['pos'].iloc[0],
        'team': player_data['currentTeamName'].iloc[0],
        'bats': player_data['batsHand'].iloc[0],
        'throws': player_data['throwsHand'].iloc[0],
        'image': player_data['playerImage'].iloc[0] if 'playerImage' in player_data.columns else None,
        'games_played': int(summary_row['games_played']),
        'team_images':team_images,
        'totals': {},
        'per_game': {},
        'rate_stats': {}
    }

    # Stat categories
    total_cols = [col for col in PLAYER_SUMMARY_DATA.columns if col.startswith('total_')]
    per_game_cols = ['PA', 'AB', 'H', 'HR', 'BB', 'K', 'HBP', 'SF', 'TB', 'RBI']
    rate_stats = ['AVG', 'OBP', 'SLG', 'OPS']

    # Populate summary data into player_info
    for col in total_cols:
        player_info['totals'][col.replace('total_', '')] = {
            'value': int(summary_row[col]),
            'rank': get_rank(col)
        }

    for col in per_game_cols:
        if col in PLAYER_SUMMARY_DATA.columns:
            player_info['per_game'][col] = {
                'value': float(summary_row[col]),
                'rank': get_rank(col)
            }

    for col in rate_stats:
        if col in PLAYER_SUMMARY_DATA.columns:
            player_info['rate_stats'][col] = {
                'value': float(summary_row[col]),
                'rank': get_rank(col)
            }

    return render_template('player_stats.html', player=player_info)

@app.route('/api/player/<int:player_id>/game_stats')
def player_game_stats_api(player_id):
    """API endpoint to get player statistics data for charts"""
    if MLB_DATA.empty or PLAYER_SUMMARY_DATA.empty:
        return jsonify({'error': 'Data not available'}), 404

    # Filter data for the selected player
    player_data = MLB_DATA[MLB_DATA['playerId'] == player_id]
    avg_data = LEAGUE_AVERAGE

    if player_data.empty or avg_data.empty:
        return jsonify({'error': 'Player not found'}), 404

    # Sort by date
    player_data = player_data.sort_values('date')
    player_data['date'] = pd.to_datetime(player_data['date'], errors='coerce')  # convert to datetime

    # Convert helper
    def convert_series_to_list(series):
        return [None if pd.isna(x) else x for x in series.tolist()]

    # Prepare time series data for charts
    stats_data = {
        'dates': player_data['date'].dt.strftime('%Y-%m-%d').tolist(),
        'oppImages': player_data['oppImage'].tolist(),

        'rate_stats': {
            'AVG': convert_series_to_list(player_data['AVG']),
            'OPS': convert_series_to_list(player_data['OPS']),
            'OBP': convert_series_to_list(player_data['OBP']) if 'OBP' in player_data.columns else [],
            'SLG': convert_series_to_list(player_data['SLG']) if 'SLG' in player_data.columns else []
        },
        'counting_stats': {
            'PA': convert_series_to_list(player_data['PA']),
            'AB': convert_series_to_list(player_data['AB']),
            'H': convert_series_to_list(player_data['H']),
            'HR': convert_series_to_list(player_data['HR']),
            'BB': convert_series_to_list(player_data['BB']),
            'K': convert_series_to_list(player_data['K']),
            'HBP': convert_series_to_list(player_data['HBP']) if 'HBP' in player_data.columns else [],
            'SF': convert_series_to_list(player_data['SF']) if 'SF' in player_data.columns else [],
            'TB': convert_series_to_list(player_data['TB']) if 'TB' in player_data.columns else [],
            'RBI': convert_series_to_list(player_data['RBI']) if 'RBI' in player_data.columns else []
        }
    }

    # Include league averages for this player
    summary_row = avg_data.iloc[0]
    stats_data['league_averages'] = {
        'AVG': float(summary_row['AVG']),
        'OPS': float(summary_row['OPS']),
        'OBP': float(summary_row['OBP']),
        'SLG': float(summary_row['SLG'])

    }

    return jsonify(stats_data)

'''
'PA': float(summary_row['PA']),
'AB': float(summary_row['AB']),
'H': float(summary_row['H']),
'HR': float(summary_row['HR']),
'BB': float(summary_row['BB']),
'K': float(summary_row['K']),
'HBP': float(summary_row['HBP']),
'SF': float(summary_row['SF']),
'TB': float(summary_row['TB']),
'RBI': float(summary_row['RBI']),
'''
@app.route('/api/players')
def get_players():
    """API endpoint to get the list of all players"""
    if MLB_DATA.empty:
        return jsonify({'error': 'Data not available'}), 404
    
    players = MLB_DATA[['playerId', 'playerFullName']].drop_duplicates().sort_values('playerFullName')
    return jsonify(players.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)