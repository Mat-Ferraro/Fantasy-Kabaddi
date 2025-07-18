from bs4 import BeautifulSoup
import pandas as pd
import requests

def GetHtml(url):
    # Send GET request
    response = requests.get(url)

    # Check if successful
    if response.status_code == 200:
        html_content = response.text
        return html_content
    else:
        print("Failed to retrieve page:", response.status_code)
        return None

# Load HTML content
def ParseHtml(file, season):
    soup = BeautifulSoup(file, "html.parser")

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
            "Successful Raids": None, "Unsuccessful Raids": None, "Empty Raids": None,
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

def RetrieveAndSaveData(url, saveLoc, season):
    html = GetHtml(url) 
    if html is not None:
        data, title = ParseHtml(html, season)

        if saveLoc is None:
            fileLoc = f"{title}.csv"
        else:
            fileLoc = saveLoc + "\\" + f"{title}.csv"
            
        data.to_csv(fileLoc, index=False, encoding="utf-8-sig")
    else:
        print("Unable to parse")

def Main():
    # Example match URL (change this to your target)
    url = "https://www.prokabaddi.com/matchcentre/5440-scorecard"
    season = "11"
    RetrieveAndSaveData(url, "C:\\ProgrammingProjects\\Kabaddi\\HTML_Test", season)    
    print("COMPLETE")

if __name__ == "__main__":
    Main()
