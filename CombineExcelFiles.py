import pandas as pd
import os

# Folder with your 12 Excel files
folder = "C:\\ProgrammingProjects\\Kabaddi\\Teams2"
output_file = "C:\\ProgrammingProjects\\Kabaddi\\All_Teams_Combined.xlsx"

combined_df = pd.DataFrame()

# Loop through each Excel file
for file in os.listdir(folder):
    if file.endswith(".xlsx"):
        file_path = os.path.join(folder, file)
        
        # Load all sheets in case some files have more than one
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            df["Source File"] = os.path.splitext(file)[0]  # Optional: track origin
            combined_df = pd.concat([combined_df, df], ignore_index=True)

# Save all data to one sheet
combined_df.to_excel(output_file, index=False, sheet_name="All Players")

print(f"Combined data saved to: {output_file}")
