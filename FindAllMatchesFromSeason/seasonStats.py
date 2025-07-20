from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def GetHtml(url, retryAttempt = 0):
    # Start headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")  # 0 = ALL, 3 = only fatal (only alert to fatal errors)
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        # Wait until the playbyplay-section loads (adjust timeout if needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "playbyplay-section"))
        )

        # Get full page source after JavaScript executes
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except Exception as e:
        print(f"⚠️ Error on attempt {retryAttempt + 1}: {e}")
        
        if retryAttempt < 3:
            time.sleep(2)
            return GetHtml(url, retryAttempt + 1)
        else: 
            return None
    finally:
        driver.quit()

# Load HTML content
def ParseHtml(soup, season):
    # Extract team names
    team_a_tag = soup.find("div", class_="match-team match-team-a")
    team_b_tag = soup.find("div", class_="match-team match-team-b")
    team_a_name = team_a_tag.find("p", class_="team-name").text.strip() if team_a_tag else "Team A"
    team_b_name = team_b_tag.find("p", class_="team-name").text.strip() if team_b_tag else "Team B"

    title_tag = soup.find("h4", class_="title")
    match_title = title_tag.text.strip() if title_tag else "Unknown Match"
    print("Match Title:", match_title)

    # Function to extract stats and position
    def extract_player_data(player_div, season):
        stats = {
            "PlayerID": None, "Team": None, "Position": None, "Player": None, "Season": None, "Match": None,
            "Total Pts": None, "Touch Pts": None, "Bonus Pts": None, "Tackle Pts": None,
            "Successful Raids": None, "Super Raids": None, "Unsuccessful Raids": None, "Empty Raids": None,
            "Successful Tackles": None, "Unsuccessful Tackles": None, "Super Tackles": None,
            "Green Card": False, "Yellow Card": False, "Red Card": False
        }
        
        stats["Season"] = season
        match_abr = match_title.replace("Match ", "")
        stats["Match"] = match_abr

        # Player name and ID
        name_tag = player_div.find("a", class_="name")
        if name_tag:
            stats["Player"] = name_tag.text.strip()
            href = name_tag.get("href", "")
            if "-profile-" in href:
                try:
                    stats["PlayerID"] = href.split("-profile-")[-1]
                except IndexError:
                    stats["PlayerID"] = None

        # Position (role)
        role_tag = player_div.find("p", class_="category")
        if role_tag:
            stats["Position"] = role_tag.text.strip()

        # Points section
        for stat in player_div.find_all("div", class_="points-item"):
            label = stat.find("p", class_="points-label").text.strip()
            value = stat.find("p", class_="points-value").text.strip()
            if label in stats:
                stats[label] = value

        # Raid stats
        raid_section = player_div.find("div", class_="raid-points-history")
        if raid_section:
            for label, value in zip(
                raid_section.find_all("p", class_="graph-label"),
                raid_section.find_all("p", class_="graph-value")
            ):
                label_text = label.text.strip()
                value_text = value.text.strip()
                if label_text in stats:
                    stats[label_text] = value_text

        # Tackle stats
        tackle_section = player_div.find("div", class_="Tackle-points-history")
        if tackle_section:
            for label, value in zip(
                tackle_section.find_all("p", class_="graph-label"),
                tackle_section.find_all("p", class_="graph-value")
            ):
                label_text = label.text.strip()
                value_text = value.text.strip()
                if label_text in stats:
                    stats[label_text] = value_text

        # Check for penalty cards
        if player_div.find("p", class_="card green-card"):
            stats["Green Card"] = True
        if player_div.find("p", class_="card yellow-card"):
            stats["Yellow Card"] = True
        if player_div.find("p", class_="card red-card"):
            stats["Red Card"] = True

        return stats

    # Helper function to gather players from team sections
    def parse_team_players(section_class, team_name, season):
        players_data = []
        for section in soup.find_all("div", class_=section_class):
            for player_div in section.find_all("div", class_="scorecard-item"):
                data = extract_player_data(player_div, season)
                if data["Player"]:  # Only append if name was found
                    data["Team"] = team_name
                    players_data.append(data)
        return players_data

    # Parse both teams
    players = []
    players.extend(parse_team_players("scorecard-list scorecard-list-a", team_a_name, season))
    players.extend(parse_team_players("scorecard-list scorecard-list-b", team_b_name, season))

    # Convert to DataFrame and show results
    df = pd.DataFrame(players)
    print(df)
    return df, match_title

def extract_super_raids_from_url(soup):
        # Find super raids
        points_histories = soup.select("div.playbyplay-section div.points-history")
        super_raid_players = []

        for history in points_histories:
            header = history.select_one("div.points-header span.sub-title")
            if header and "SUPER RAID" in header.text.upper():
                player_tag = history.select_one("div.points-information span.player-name")
                if player_tag:
                    super_raid_players.append(player_tag.text.strip())

        # Count and save
        counts = Counter(super_raid_players)
        df = pd.DataFrame(counts.items(), columns=["Player Name", "Super Raid Count"])     
        print(f"Found {len(df)} Super Raid records")
        return df


def RetrieveAndSaveData(url, saveLoc, season):
    html = GetHtml(url) 
    if html is not None:
        data, title = ParseHtml(html, season)
        superRaids = extract_super_raids_from_url(html) 

        # Initialize all Super Raids to 0
        data["Super Raids"] = 0

        # Loop through each super raid record
        for _, super_row in superRaids.iterrows():
            super_name = super_row["Player Name"].strip().lower()
            super_count = super_row["Super Raid Count"]

            # Loop through player data to match and update
            for i, player_row in data.iterrows():
                player_name = player_row["Player"]
                touch_pts = player_row.get("Touch Pts")

                if player_name and player_name.strip().lower() == super_name:
                    try:
                        # Attempt to convert Touch Pts to integer for comparison
                        touch_pts_val = int(touch_pts)
                    except (ValueError, TypeError):
                        touch_pts_val = 0  # Treat missing or invalid as 0

                    # since we can't confirm the player by their name 100% of the time
                    # we will add a check to verify this player has at least 3 touch points
                    # this is a bandaid, but covers the edge case of duplicate names well enough
                    # the best way to handle this, would be by looking up the player ID, but we don't have access to the id
                    # of the player who scored the super raid
                    if touch_pts_val >= 3:
                        data.at[i, "Super Raids"] = super_count
                        break  # Stop searching once we've matched this player

        if saveLoc is None:
            fileLoc = f"{title}.csv"
        else:
            
            if "Final" in title or "Eliminator" in title:
                fileLoc = saveLoc + f"\\Playoffs\\{title}.csv"
            else:
                fileLoc = saveLoc + f"\\{title}.csv"
            
        with open(fileLoc, 'w', encoding='utf-8-sig', newline='') as f:
            data.to_csv(f, index=False)
        # data.to_csv(fileLoc, index=False, encoding="utf-8-sig")
    else:
        print("Unable to parse")


###################################################################
##################################################################

def extract_season_from_html(soup):
    # with open(html_path, "r", encoding="utf-8") as file:
    #     soup = BeautifulSoup(file, "html.parser")

    # Step 1: Try narrow path using CSS selectors
    tag = soup.select_one("layout-wrapper waf-body filter-section filter-wrap waf-select-box selected-title title")

    if tag and "season" in tag.text.lower():
        return tag.text.strip()

    # Step 2: Fallback: Look for any <title> or <div> or <span> with "Season" in it
    possible_tags = soup.find_all(string=lambda t: "season" in t.lower())
    for text in possible_tags:
        clean_text = text.strip()
        if clean_text.lower().startswith("season"):
            clean_text = clean_text.replace("Season ", "")
            return clean_text

    return None

def ParseSeasonStatsHTML(html, saveFolder):
    with open(html, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    season = extract_season_from_html(soup)

    # Locate each match container
    fixtures = soup.find_all("div", class_="fixtures-element")
    match_data = []

    for fixture in fixtures:
        # Match Number
        match_number_tag = fixture.find("p", class_="match-count")
        match_number = match_number_tag.text.strip() if match_number_tag else ""

        # Date (comes from fixtures-head above this block)
        date_tag = fixture.find_previous("div", class_="fixtures-head")
        date_title = date_tag.find("h2", class_="fixtures-title") if date_tag else None
        match_date = date_title.text.strip() if date_title else ""

        # Location
        location_tag = fixture.find("div", class_="element element3")
        location = location_tag.find("p", class_="match-place").text.strip() if location_tag and location_tag.find("p", class_="match-place") else ""

        # Match link + teams + scores
        match_links = fixture.find_all("a", href=True)
        for match in match_links:
            href = match["href"]
            if "/matchcentre/" in href and "scorecard" in href:
                full_url = "https://www.prokabaddi.com" + href

                # Find team names using precise DOM structure
                team_1_tag = match.select_one("div.team.team-a div.team-info p.team-name")
                team_2_tag = match.select_one("div.team.team-b div.team-info p.team-name")

                team_1 = team_1_tag.text.strip() if team_1_tag else ""
                team_2 = team_2_tag.text.strip() if team_2_tag else ""

                # Scores
                team_a_div = match.find("div", class_="team team-a")
                score_1 = team_a_div.find("p", class_="score").text.strip() if team_a_div and team_a_div.find("p", class_="score") else ""

                team_b_div = match.find("div", class_="team team-b")
                score_2 = team_b_div.find("p", class_="score").text.strip() if team_b_div and team_b_div.find("p", class_="score") else ""

                match_data.append({
                    "Match Number": match_number,
                    "Date": match_date,
                    "Team 1": team_1,
                    "Score 1": score_1,
                    "Score 2": score_2,
                    "Team 2": team_2,
                    "Location": location,
                    "URL": full_url,
                })
                
                try:
                    RetrieveAndSaveData(full_url, saveFolder, season)
                except Exception as e:
                    print(f"Failed to scrape {full_url}: {e}")

    return pd.DataFrame(match_data)

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

def Main():
    
    for i in range(11, 0 , -1):
        season = f"Season{i}"

        # Path to your HTML file
        html_path = f"C:\\ProgrammingProjects\\Kabaddi\\{season}-Matches.html"  
        
        saveLoc = f"C:\\ProgrammingProjects\\Kabaddi\\Fantasy-Kabaddi\\{season}"
        scores_path = saveLoc + "\\FinalScores"
        playoff_path = scores_path + "\\Playoffs"
        os.makedirs(playoff_path, exist_ok=True)
        
        finalScores = ParseSeasonStatsHTML(html_path, scores_path)

        finalScores.to_csv(f"{saveLoc}\\Kabaddi_{season}_MatchResults.csv", index=False)
        print("Saved to kabaddi_match_details_complete.csv with", len(finalScores), "matches.")
        
        combine_csv_files(scores_path, saveLoc + f"\\Kabaddi_{season}_AllPlayerStats.csv")
        print("COMPLETE")
    


if __name__ == "__main__":
    Main()