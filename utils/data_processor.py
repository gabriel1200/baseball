"""
Data processor utility for MLB Stats Visualizer
Provides functions for processing and analyzing MLB player data
"""

import pandas as pd
import numpy as np
from datetime import datetime


def load_and_validate_csv(file_path):
    """
    Load a CSV file and validate that it contains the required fields
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: DataFrame containing the validated data
    """
    try:
        df = pd.read_csv(file_path)
        
        # Check for required fields
        required_fields = [
            'playerId', 'playerFullName', 'date', 
            'PA', 'AB', 'H', 'HR', 'BB', 'K', 
            'HBP', 'SF', 'TB', 'RBI'
        ]
        
        for field in required_fields:
            if field not in df.columns:
                raise ValueError(f"Required field '{field}' not found in the CSV file")
        
        return df
    except Exception as e:
        raise Exception(f"Error loading or validating CSV: {str(e)}")


def calculate_rate_stats(df):
    """
    Calculate rate stats (AVG, OBP, SLG, OPS) if they don't exist in the data
    
    Args:
        df (pandas.DataFrame): DataFrame containing the player data
        
    Returns:
        pandas.DataFrame: DataFrame with calculated rate stats
    """
    # Make a copy to avoid modifying the original
    df_with_stats = df.copy()
    
    # Calculate AVG if it doesn't exist
    if 'AVG' not in df_with_stats.columns:
        df_with_stats['AVG'] = df_with_stats['H'] / df_with_stats['AB']
        df_with_stats['AVG'] = df_with_stats['AVG'].replace([np.inf, -np.inf], np.nan)
        
    # Calculate OBP if it doesn't exist
    if 'OBP' not in df_with_stats.columns:
        # OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
        df_with_stats['OBP'] = (df_with_stats['H'] + df_with_stats['BB'] + df_with_stats['HBP']) / \
                               (df_with_stats['AB'] + df_with_stats['BB'] + df_with_stats['HBP'] + df_with_stats['SF'])
        df_with_stats['OBP'] = df_with_stats['OBP'].replace([np.inf, -np.inf], np.nan)
        
    # Calculate SLG if it doesn't exist
    if 'SLG' not in df_with_stats.columns:
        # SLG = TB / AB
        df_with_stats['SLG'] = df_with_stats['TB'] / df_with_stats['AB']
        df_with_stats['SLG'] = df_with_stats['SLG'].replace([np.inf, -np.inf], np.nan)
        
    # Calculate OPS if it doesn't exist
    if 'OPS' not in df_with_stats.columns:
        # OPS = OBP + SLG
        if 'OBP' in df_with_stats.columns and 'SLG' in df_with_stats.columns:
            df_with_stats['OPS'] = df_with_stats['OBP'] + df_with_stats['SLG']
        else:
            # Calculate using the components
            on_base = (df_with_stats['H'] + df_with_stats['BB'] + df_with_stats['HBP']) / \
                      (df_with_stats['AB'] + df_with_stats['BB'] + df_with_stats['HBP'] + df_with_stats['SF'])
            slugging = df_with_stats['TB'] / df_with_stats['AB']
            df_with_stats['OPS'] = on_base + slugging
            
        df_with_stats['OPS'] = df_with_stats['OPS'].replace([np.inf, -np.inf], np.nan)
    
    return df_with_stats


def get_player_summary(df, player_id):
    """
    Get a summary of a player's statistics
    
    Args:
        df (pandas.DataFrame): DataFrame containing the player data
        player_id (int): ID of the player to get the summary for
        
    Returns:
        dict: Dictionary containing the player's summary statistics
    """
    player_data = df[df['playerId'] == player_id]
    
    if player_data.empty:
        return None
    
    # Get player info
    player_info = {
        'id': player_id,
        'name': player_data['playerFullName'].iloc[0],
        'position': player_data['pos'].iloc[0] if 'pos' in player_data.columns else 'Unknown',
        'team': player_data['currentTeamName'].iloc[0] if 'currentTeamName' in player_data.columns else 'Unknown',
        'image': player_data['playerImage'].iloc[0] if 'playerImage' in player_data.columns else None
    }
    
    # Calculate career totals
    totals = {
        'games': len(player_data),
        'PA': int(player_data['PA'].sum()),
        'AB': int(player_data['AB'].sum()),
        'H': int(player_data['H'].sum()),
        'HR': int(player_data['HR'].sum()),
        'BB': int(player_data['BB'].sum()),
        'K': int(player_data['K'].sum()),
        'TB': int(player_data['TB'].sum()) if 'TB' in player_data.columns else None,
        'RBI': int(player_data['RBI'].sum()) if 'RBI' in player_data.columns else None,
    }
    
    # Calculate career rate stats
    if totals['AB'] > 0:
        totals['AVG'] = totals['H'] / totals['AB']
        totals['SLG'] = totals['TB'] / totals['AB'] if totals['TB'] is not None else None
    else:
        totals['AVG'] = None
        totals['SLG'] = None
    
    denominator = totals['AB'] + totals['BB'] + (player_data['HBP'].sum() if 'HBP' in player_data.columns else 0) + (player_data['SF'].sum() if 'SF' in player_data.columns else 0)
    if denominator > 0:
        totals['OBP'] = (totals['H'] + totals['BB'] + (player_data['HBP'].sum() if 'HBP' in player_data.columns else 0)) / denominator
    else:
        totals['OBP'] = None
    
    if totals['OBP'] is not None and totals['SLG'] is not None:
        totals['OPS'] = totals['OBP'] + totals['SLG']
    else:
        totals['OPS'] = None
    
    return {
        'info': player_info,
        'totals': totals,
        'data': player_data.sort_values('date').to_dict('records')
    }


def get_player_time_series(df, player_id):
    """
    Get time series data for a player
    
    Args:
        df (pandas.DataFrame): DataFrame containing the player data
        player_id (int): ID of the player to get the time series for
        
    Returns:
        dict: Dictionary containing the player's time series data
    """
    player_data = df[df['playerId'] == player_id].sort_values('date')
    
    if player_data.empty:
        return None
    
    # Format dates to be more readable
    dates = [format_date(date_str) for date_str in player_data['date']]
    
    # Prepare rate stats
    rate_stats = {
        'AVG': player_data['AVG'].tolist() if 'AVG' in player_data.columns else [],
        'OBP': player_data['OBP'].tolist() if 'OBP' in player_data.columns else [],
        'SLG': player_data['SLG'].tolist() if 'SLG' in player_data.columns else [],
        'OPS': player_data['OPS'].tolist() if 'OPS' in player_data.columns else []
    }
    
    # Prepare counting stats
    counting_stats = {
        'PA': player_data['PA'].tolist(),
        'AB': player_data['AB'].tolist(),
        'H': player_data['H'].tolist(),
        'HR': player_data['HR'].tolist(),
        'BB': player_data['BB'].tolist(),
        'K': player_data['K'].tolist(),
        'HBP': player_data['HBP'].tolist() if 'HBP' in player_data.columns else [],
        'SF': player_data['SF'].tolist() if 'SF' in player_data.columns else [],
        'TB': player_data['TB'].tolist() if 'TB' in player_data.columns else [],
        'RBI': player_data['RBI'].tolist() if 'RBI' in player_data.columns else []
    }
    
    return {
        'dates': dates,
        'rate_stats': rate_stats,
        'counting_stats': counting_stats
    }


def format_date(date_str):
    """
    Format a date string to MM/DD/YYYY format
    
    Args:
        date_str (str): Date string to format
        
    Returns:
        str: Formatted date string
    """
    try:
        # Try parsing with various formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%m/%d/%Y')
            except ValueError:
                continue
                
        # If none of the formats work, return the original string
        return date_str
    except:
        return date_str