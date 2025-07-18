from bs4 import BeautifulSoup
import pandas as pd


def ParseHTML(html):
    from bs4 import BeautifulSoup
    import pandas as pd

    with open(html, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

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

                team_names = match.find_all("p", class_="team-name")

                team_a_div = match.find("div", class_="team team-a")
                score_1 = team_a_div.find("p", class_="score").text.strip() if team_a_div and team_a_div.find("p", class_="score") else ""

                team_b_div = match.find("div", class_="team team-b")
                score_2 = team_b_div.find("p", class_="score").text.strip() if team_b_div and team_b_div.find("p", class_="score") else ""

                match_data.append({
                    "Match Number": match_number,
                    "Date": match_date,
                    "Team 1": team_names[0].text.strip() if len(team_names) > 0 else "",
                    "Score 1": score_1,
                    "Score 2": score_2,
                    "Team 2": team_names[1].text.strip() if len(team_names) > 1 else "",
                    "Location": location,
                    "URL": full_url,
                })

    return pd.DataFrame(match_data)

def Main():
    # Path to your HTML file
    html_path = "C:\\ProgrammingProjects\\Kabaddi\\Matches.html"
    data = ParseHTML(html_path)

    data.to_csv("C:\\ProgrammingProjects\\Kabaddi\\kabaddi_match_details_complete.csv", index=False)
    print("Saved to kabaddi_match_details_complete.csv with", len(data), "matches.")



if __name__ == "__main__":
    Main()