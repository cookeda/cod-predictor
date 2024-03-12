import pandas as pd  # For data manipulation
import numpy as np  # For numerical operations
#from sklearn.preprocessing import LabelEncoder  # For encoding categorical variables
#from sklearn.preprocessing import MinMaxScaler  # For normalizing features
from datetime import datetime  # For handling date and time
import json
import matplotlib.pyplot as plt
import seaborn as sns


# Load data from the JSON file
with open("matches_data.json", "r") as file:
    data = json.load(file)

# Initialize an empty list to hold all the map outcomes
all_maps = []

# Loop through each tournament to extract match details
for tournament in data:  # Each item in data is a tournament
    for match in tournament['matches']:  # Accessing matches within a tournament
        for map_detail in match['maps']:  # Now correctly accessing maps within matches
            # Create a dictionary for each map outcome, adjusting to the correct structure
            map_outcome = {
                'team1': match['team1'],
                'team1_score': match['team1_score'],
                'team2': match['team2'],
                'team2_score': match['team2_score'],
                'map_name': map_detail['map_name'],
                'mode_name': map_detail['mode_name'],
                'map_winner': map_detail['map_winner'],
                'team1_score': map_detail['team1_score'],
                'team2_score': map_detail['team2_score']
            }
            # Append the map outcome to the list
            all_maps.append(map_outcome)

# Convert the corrected list of map outcomes into a pandas DataFrame
df_maps = pd.DataFrame(all_maps)

# Display the first few rows to ensure it looks as expected this time
# Display the first few rows to ensure it looks as expected
print(df_maps.head())