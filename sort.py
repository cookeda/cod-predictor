import pandas as pd  # For data manipulation
import numpy as np  # For numerical operations
from sklearn.preprocessing import LabelEncoder  # For encoding categorical variables
from sklearn.preprocessing import MinMaxScaler  # For normalizing features
from datetime import datetime  # For handling date and time
import json

# Load data from the JSON file
with open("matches_data.json", "r") as file:
    data = json.load(file)

# We will start by creating a flat structure from the nested JSON, focusing on relevant features for prediction

# Initialize an empty list to hold the flattened data
flattened_data = []

# Iterate through the data to flatten it
for tournament in data:
    for match in tournament['matches']:
        for map_info in match['maps']:
            record = {
                'major':tournament['tournament']['major'],
                'format': tournament['tournament']['format'],
                'team1': match['team1'],
                'team1_score': match['team1_score'],
                'team2': match['team2'],
                'team2_score': match['team2_score'],
                'map_name': map_info['map_name'],
                'mode_name': map_info['mode_name'],
                'map_winner': map_info['map_winner'],
                'team1_map_score': map_info['team1_score'],
                'team2_map_score': map_info['team2_score'],
                'date': match['date']
            }
            flattened_data.append(record)

# Convert the list of dictionaries into a pandas DataFrame
df = pd.DataFrame(flattened_data)

# Calculating Margin of Victory
df['margin_of_victory'] = abs(df['team1_map_score'] - df['team2_map_score'])

# # Win percent map
# df['win_percent_map'] = df.groupby('map_name')['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent mode
# df['win_percent_mode'] = df.groupby('mode_name')['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent by map and mode
# df['win_percent_map_mode'] = df.groupby(['map_name', 'mode_name'])['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent by map/mode/format
# df['win_percent_map_mode_format'] = df.groupby(['map_name', 'mode_name', 'format'])['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent by map/mode/major
# df['win_percent_map_mode_major'] = df.groupby(['map_name', 'mode_name', 'major'])['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent by map/major
# df['win_percent_map_major'] = df.groupby(['map_name', 'major'])['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent by mode/major
# df['win_percent_mode_major'] = df.groupby(['mode_name', 'major'])['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent by mode/format
# df['win_percent_mode_format'] = df.groupby(['mode_name', 'format'])['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Win percent by map/format
# df['win_percent_map_format'] = df.groupby(['map_name', 'format'])['map_winner'].transform(lambda x: x.eq(df['map_winner']).mean())

# # Average MOV per mode/map
# df['avg_mov_per_mode_map'] = df.groupby(['mode_name', 'map_name'])['margin_of_victory'].transform('mean')

# # Average MOV per major/mode/map
# df['avg_mov_per_major_mode_map'] = df.groupby(['major', 'mode_name', 'map_name'])['margin_of_victory'].transform('mean')

# # Average MOV per format/mode/map
# df['avg_mov_per_format_mode_map'] = df.groupby(['format', 'mode_name', 'map_name'])['margin_of_victory'].transform('mean')

# # Average MOV per format/map
# df['avg_mov_per_format_map'] = df.groupby(['format', 'map_name'])['margin_of_victory'].transform('mean')

# # Average MOV per format/mode
# df['avg_mov_per_format_mode'] = df.groupby(['format', 'mode_name'])['margin_of_victory'].transform('mean')

# # Average MOV per major/mode
# df['avg_mov_per_major_mode'] = df.groupby(['major', 'mode_name'])['margin_of_victory'].transform('mean')

# # Average MOV per major/map
# df['avg_mov_per_major_map'] = df.groupby(['major', 'map_name'])['margin_of_victory'].transform('mean')

# Encoding categorical variables
label_encoders = {}  # Dictionary to store label encoders for each categorical column for potential inverse transform
categorical_columns = ['major', 'format', 'team1', 'team2', 'map_name', 'mode_name', 'map_winner']
for column in categorical_columns:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
    label_encoders[column] = le

# Normalizing numerical features
scaler = MinMaxScaler()
numerical_columns = ['team1_score', 'team2_score', 'team1_map_score', 'team2_map_score']
df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

# Calculate overall win rates for teams
df['team_win'] = (df['map_winner'] == df['team1']).astype(int)  # Assuming map_winner is the encoded team ID
team_win_rates = df.groupby('team1')['team_win'].mean().reset_index(name='overall_win_rate')

# Calculate win rates per map/mode/format combination for team1
combination_win_rates = df.groupby(['team1', 'map_name', 'mode_name', 'major'])['team_win'].mean().reset_index(name='combination_win_rate')

# Merge overall win rates with combination-specific win rates for team1
team_strengths = pd.merge(combination_win_rates, team_win_rates, left_on='team1', right_on='team1', how='left')

# Calculate the relative strength indicator
team_strengths['relative_strength'] = team_strengths['combination_win_rate'] - team_strengths['overall_win_rate']

# Repeat the process for team2 as needed, adjusting the 'team_win' calculation accordingly

# Normalize these new features
features_to_normalize = ['combination_win_rate', 'overall_win_rate', 'relative_strength']
team_strengths[features_to_normalize] = scaler.fit_transform(team_strengths[features_to_normalize])

# Merge these metrics back into the main DataFrame
df = pd.merge(df, team_strengths, on=['team1', 'map_name', 'mode_name', 'major'], how='left')

# Consider doing the same for team2, adjusting column names and calculations as necessary

print(df.head())