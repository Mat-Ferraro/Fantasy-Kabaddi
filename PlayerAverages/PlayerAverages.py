import pandas as pd

def list_unique_player_ids(file_path):
    df = pd.read_csv(file_path)
    unique_ids = df["PlayerID"].dropna().unique()
    unique_ids = sorted([int(pid) for pid in unique_ids if str(pid).isdigit()])
    return unique_ids

def summarize_player_stats(df, player_id):
    df_player = df[df["PlayerID"] == player_id].copy()

    numeric_fields = [
        "Total Pts", "Touch Pts", "Bonus Pts", "Tackle Pts",
        "Successful Raids", "Super Raids", "Unsuccessful Raids", "Empty Raids",
        "Successful Tackles", "Unsuccessful Tackles", "Super Tackles"
    ]

    summary = {
        "PlayerID": player_id,
        "Player": df_player["Player"].iloc[0] if not df_player["Player"].isnull().all() else "Unknown",
        "Games Played": len(df_player)
    }

    for field in numeric_fields:
        df_player[field] = pd.to_numeric(df_player[field], errors="coerce")
        summary[field] = df_player[field].sum()

    # Count total green cards
    if "Green Card" in df_player.columns:
        summary["Total Green Cards"] = df_player["Green Card"].astype(str).str.upper().eq("TRUE").sum()
    else:
        summary["Total Green Cards"] = 0
        
    # Count total yellow cards
    if "Yellow Card" in df_player.columns:
        summary["Total Yellow Cards"] = df_player["Yellow Card"].astype(str).str.upper().eq("TRUE").sum()
    else:
        summary["Total Yellow Cards"] = 0
        
    # Count total red cards
    if "Red Card" in df_player.columns:
        summary["Total Red Cards"] = df_player["Red Card"].astype(str).str.upper().eq("TRUE").sum()
    else:
        summary["Total Red Cards"] = 0

    return summary

def main():
    path = "C:\\ProgrammingProjects\\Kabaddi\\Fantasy-Kabaddi\\Season11\\Kabaddi_Season11_AllPlayerStats.csv"
    output_csv = "C:\\ProgrammingProjects\\Kabaddi\\Fantasy-Kabaddi\\Season11\\Kabaddi_Season11_Player_Summary_Stats.csv"

    df = pd.read_csv(path)
    player_ids = list_unique_player_ids(path)

    all_summaries = []
    for pid in player_ids:
        summary = summarize_player_stats(df, pid)
        all_summaries.append(summary)

    summary_df = pd.DataFrame(all_summaries)

    # Compute averages per game
    for field in [
        "Total Pts", "Touch Pts", "Bonus Pts", "Tackle Pts",
        "Successful Raids", "Super Raids", "Unsuccessful Raids", "Empty Raids",
        "Successful Tackles", "Unsuccessful Tackles", "Super Tackles"
    ]:
        summary_df[f"Average {field}"] = summary_df[field] / summary_df["Games Played"]

    # Add ranking columns
    summary_df["Total Pts Rank"] = summary_df["Total Pts"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Total Pts Rank"] = summary_df["Average Total Pts"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Touch Pts Rank"] = summary_df["Touch Pts"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Touch Pts Rank"] = summary_df["Average Touch Pts"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Bonus Pts Rank"] = summary_df["Bonus Pts"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Bonus Pts Rank"] = summary_df["Average Bonus Pts"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Tackle Pts Rank"] = summary_df["Tackle Pts"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Tackle Pts Rank"] = summary_df["Average Tackle Pts"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Successful Raids Rank"] = summary_df["Successful Raids"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Successful Raids Rank"] = summary_df["Average Successful Raids"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Super Raids Rank"] = summary_df["Super Raids"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Super Raids Rank"] = summary_df["Average Super Raids"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Unsuccessful Raids Rank"] = summary_df["Unsuccessful Raids"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Unsuccessful Raids Rank"] = summary_df["Average Unsuccessful Raids"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Empty Raids Rank"] = summary_df["Empty Raids"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Empty Raids Rank"] = summary_df["Average Empty Raids"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Successful Tackles Rank"] = summary_df["Successful Tackles"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Successful Tackles Rank"] = summary_df["Average Successful Tackles"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Unsuccessful Tackles Rank"] = summary_df["Unsuccessful Tackles"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Unsuccessful Tackles Rank"] = summary_df["Average Unsuccessful Tackles"].rank(method="dense", ascending=False).astype(int)
    
    summary_df["Super Tackles Rank"] = summary_df["Super Tackles"].rank(method="dense", ascending=False).astype(int)
    summary_df["Average Super Tackles Rank"] = summary_df["Average Super Tackles"].rank(method="dense", ascending=False).astype(int)
    

    # Sort and save
    summary_df.sort_values(by="Total Pts", ascending=False, inplace=True)
    summary_df.to_csv(output_csv, index=False)
    print(f"✅ Player summaries with averages saved to: {output_csv}")

if __name__ == "__main__":
    main()







