import os
import pandas as pd

def combine_csv_files(input_folder, output_file):
    all_dataframes = []

    # List all CSV files in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_folder, filename)
            try:
                df = pd.read_csv(file_path)
                all_dataframes.append(df)
                print(f"✅ Loaded: {filename}")
            except Exception as e:
                print(f"⚠️ Could not load {filename}: {e}")

    # Concatenate all dataframes
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        combined_df.to_csv(output_file, index=False)
        print(f"\n🎉 Combined {len(all_dataframes)} CSV files into: {output_file}")
    else:
        print("❌ No CSV files found to combine.")

# === CONFIGURE THIS ===
season = "Season10"
input_folder = f"C:\\ProgrammingProjects\\Kabaddi\\Fantasy-Kabaddi\\{season}\\FinalScores"
output_file = f"C:\\ProgrammingProjects\\Kabaddi\\Fantasy-Kabaddi\\{season}\\AllPlayerStats_{season}.csv"

if __name__ == "__main__":
    combine_csv_files(input_folder, output_file)
