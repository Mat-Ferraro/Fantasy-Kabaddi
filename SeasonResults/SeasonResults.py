import pandas as pd

def determine_results(input_csv, output_csv):
    # Load CSV
    df = pd.read_csv(input_csv)

    # Filter only rows with "Match" in the Match Number
    df = df[df['Match Number'].astype(str).str.contains("Match", na=False)]

    # Initialize dictionaries to accumulate stats
    result_counts = {}
    points_for = {}
    points_against = {}

    for _, row in df.iterrows():
        team1 = row['Team 1']
        score1 = row['Score 1']
        team2 = row['Team 2']
        score2 = row['Score 2']

        if pd.isna(score1) or pd.isna(score2):
            continue

        # Ensure each team has an entry
        for team in [team1, team2]:
            if team not in result_counts:
                result_counts[team] = {'Win': 0, 'Loss': 0, 'Draw': 0}
                points_for[team] = 0
                points_against[team] = 0

        # Update results
        if score1 > score2:
            result_counts[team1]['Win'] += 1
            result_counts[team2]['Loss'] += 1
        elif score2 > score1:
            result_counts[team2]['Win'] += 1
            result_counts[team1]['Loss'] += 1
        else:
            result_counts[team1]['Draw'] += 1
            result_counts[team2]['Draw'] += 1

        # Update points
        points_for[team1] += score1
        points_against[team1] += score2

        points_for[team2] += score2
        points_against[team2] += score1

    # Build final DataFrame
    summary_data = []
    for team in result_counts:
        wins = result_counts[team]['Win']
        losses = result_counts[team]['Loss']
        draws = result_counts[team]['Draw']
        pf = points_for[team]
        pa = points_against[team]
        summary_data.append([team, wins, losses, draws, pf, pa])

    summary_df = pd.DataFrame(
        summary_data,
        columns=["Team", "Win", "Loss", "Draw", "Points For", "Points Against"]
    ).set_index("Team")

    # Add average columns
    total_games = summary_df["Win"] + summary_df["Loss"] + summary_df["Draw"]
    summary_df["Average Points For"] = summary_df["Points For"] / total_games
    summary_df["Average Points Against"] = summary_df["Points Against"] / total_games

    # Add ranking columns
    summary_df["Points For Rank"] = summary_df["Points For"].rank(method="dense", ascending=False).astype(int)
    summary_df["Points Against Rank"] = summary_df["Points Against"].rank(method="dense", ascending=True).astype(int)

    # Save to CSV
    summary_df.to_csv(output_csv)

def Main():
    csv_file = "C:\\ProgrammingProjects\\Kabaddi\\Fantasy-Kabaddi\\Season11\\Kabaddi_Season11_MatchResults.csv"
    output_file = "C:\\ProgrammingProjects\\Kabaddi\\Fantasy-Kabaddi\\Season11\\Kabaddi_Season11_SeasonResults.csv"
    
    determine_results(csv_file, output_file)
    print("✅ Team records written to:", output_file)

if __name__ == "__main__":
    Main()
