import pandas as pd
import json

with open("matches_data.json", "r") as file:
    data = json.load(file)
# Assuming 'data' is already loaded from 'matches_data.json'
matches_list = []
for tournament in data:
    for match in tournament['matches']:
        for game in match['maps']:
            matches_list.append({
                'tournament': tournament['tournament']['major'],
                'format': tournament['tournament']['format'],
                'team1': match['team1'],
                'team2': match['team2'],
                'team1_score': game['team1_score'],
                'team2_score': game['team2_score'],
                'map_name': game['map_name'],
                'mode_name': game['mode_name'],
                'map_winner': game['map_winner']
            })

# Convert the list of matches to a DataFrame
matches_df = pd.DataFrame(matches_list)

def update_elo(winner_elo, loser_elo, K=32):
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + K * (1 - expected_winner)
    new_loser_elo = loser_elo - K * (1 - expected_winner)
    return new_winner_elo, new_loser_elo

def predict_score(team1_elo, team2_elo):
    expected_team1 = 1 / (1 + 10 ** ((team2_elo - team1_elo) / 400))
    expected_team2 = 1 - expected_team1
    return expected_team1, expected_team2

def generate_elo_rankings(matches):
    elo_ratings = {}
    for _, row in matches.iterrows():
        map_mode = (row['map_name'], row['mode_name'])
        team1, team2 = row['team1'], row['team2']
        team1_score, team2_score = row['team1_score'], row['team2_score']

        if map_mode not in elo_ratings:
            elo_ratings[map_mode] = {team: 1500 for team in set(matches['team1']).union(set(matches['team2']))}
        
        team1_elo = elo_ratings[map_mode].get(team1, 1500)
        team2_elo = elo_ratings[map_mode].get(team2, 1500)

        if team1_score > team2_score:
            team1_new_elo, team2_new_elo = update_elo(team1_elo, team2_elo)
        else:
            team2_new_elo, team1_new_elo = update_elo(team2_elo, team1_elo)
        
        elo_ratings[map_mode][team1] = team1_new_elo
        elo_ratings[map_mode][team2] = team2_new_elo

    return elo_ratings

# Generate Elo rankings
elo_rankings = generate_elo_rankings(matches_df)
def select_map(maps):
    print("Select a Map:")
    for i, map_name in enumerate(maps):
        print(f"{i+1}: {map_name}")
    selection = int(input("Enter the number of your choice: ")) - 1
    selected_map = maps[selection]
    return selected_map

def select_mode(modes):
    print("\nSelect a Mode:")
    for i, mode_name in enumerate(modes):
        print(f"{i+1}: {mode_name}")
    selection = int(input("Enter the number of your choice: ")) - 1
    selected_mode = modes[selection]
    return selected_mode

def select_team(teams):
    print("\nSelect Team 1:")
    for i, team in enumerate(teams):
        print(f"{i+1}: {team}")
    team1_selection = int(input("Enter the number of your choice: ")) - 1

    print("\nSelect Team 2:")
    for i, team in enumerate(teams):
        if i != team1_selection:
            print(f"{i+1}: {team}")
    team2_selection = int(input("Enter the number of your choice: ")) - 1

    return teams[team1_selection], teams[team2_selection]

# Example usage:
maps = sorted(list(set(matches_df['map_name'])))  # Assuming matches_df is your DataFrame
modes = sorted(list(set(matches_df['mode_name'])))
teams = sorted(list(set(matches_df['team1']).union(set(matches_df['team2']))))

selected_map = select_map(maps)
selected_mode = select_mode(modes)
team1, team2 = select_team(teams)

# Assuming elo_rankings is already calculated
map_mode = (selected_map, selected_mode)
team1_elo, team2_elo = elo_rankings[map_mode].get(team1, 1500), elo_rankings[map_mode].get(team2, 1500)
expected_team1, expected_team2 = predict_score(team1_elo, team2_elo)

print(f"\nPredicted outcome for {team1} vs. {team2} on {selected_map} {selected_mode}: \n{team1} win probability: {expected_team1}, \n{team2} win probability: {expected_team2}")