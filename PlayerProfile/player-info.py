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
    
    
# Load the HTML file
# with open("C:\\ProgrammingProjects\\Kabaddi\\Kabaddi_TeamData.html", "r", encoding="utf-8") as file:
def ParseHtml(file):
    soup = BeautifulSoup(file, "html.parser")

    # Extract team name
    team_name_tag = soup.find("h4", class_="content-title")
    team_name = team_name_tag.get_text(strip=True) if team_name_tag else "Unknown"

    # Extract player information
    players = []
    squad_wrappers = soup.find_all("div", class_="squad-wrapper")

    for wrapper in squad_wrappers:
        # Get PlayerID from <a data-id=""> if available, otherwise from <div>
        a_tag = wrapper.find("a", attrs={"data-id": True})
        player_id = a_tag["data-id"] if a_tag and a_tag.has_attr("data-id") else wrapper.get("data-id", "Unknown")

        first_name_tag = wrapper.find("p", class_="name first-name")
        last_name_tag = wrapper.find("p", class_="name last-name")
        position_tag = wrapper.find("p", class_="squad-category")

        player_name = f"{first_name_tag.get_text(strip=True) if first_name_tag else ''} {last_name_tag.get_text(strip=True) if last_name_tag else ''}".strip()
        position = position_tag.get_text(strip=True) if position_tag else "Unknown"

        # Get player URL from <div class="squad-footer"> → <a href="...">
        footer = wrapper.find("div", class_="squad-footer")
        link = footer.find("a", href=True) if footer else None
        player_url = f"https://www.prokabaddi.com{link['href']}" if link else "N/A"

        players.append({
            "PlayerID": player_id,
            "Team Name": team_name,
            "Position": position,
            "Player Name": player_name,
            "Player URL": player_url
        })

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # Show or export the result
    print(df)
    return df, team_name

def Main():
    
    url = "https://www.prokabaddi.com/teams/up-yoddha-profile-30"
    html = GetHtml(url)
    data, team = ParseHtml(html)
    
    team = team.replace(" ", "_")
    data.to_excel(f"C:\\ProgrammingProjects\\Kabaddi\\Teams2\\{team}_Players.xlsx", index=False)

if __name__ == "__main__":
    Main()