import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

standings_url = 'https://fbref.com/en/comps/12/La-Liga-Stats'
standings_data = requests.get(standings_url)
soup = BeautifulSoup(standings_data.text, 'lxml')
standings_table = soup.select('table.stats_table')[0]
links = [l.get('href') for l in standings_table.find_all('a')]
links = [l for l in links if '/squads' in l]
team_urls = [f"https://fbref.com{l}" for l in links]
team_url = team_urls[3]
data = requests.get(team_url)
matches = pd.read_html(data.text, match='Scores & Fixtures')[0]
soup = BeautifulSoup(data.text, 'lxml')
links = [l.get('href') for l in soup.find_all('a')]
links = [l for l in links if l and '/all_comps/shooting/' in l]
shooting_data = requests.get(f"https://fbref.com{links[0]}")
shooting = pd.read_html(shooting_data.text, match='Shooting')[0]
shooting.columns = shooting.columns.droplevel()
team_data = matches.merge(
    shooting[['Date', 'Sh', 'SoT', 'SoT%', 'G/Sh', 'Dist', 'FK', 'PK', 'PKatt']], on="Date")
team_name = team_url.split('/')[-1].replace('-Stats', '').replace('-', " ")
team_data = team_data[team_data['Comp'] == 'La Liga']
years = list(range(2024, 2019, -1))
all_matches = []
standings_url = 'https://fbref.com/en/comps/12/La-Liga-Stats'
for year in years:
    standings_data = requests.get(standings_url)
    soup = BeautifulSoup(standings_data.text, 'lxml')
    standings_table = soup.select('table.stats_table')[0]

    links = [l.get('href') for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]

    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"

    for team_url in team_urls:
        team_name = team_url.split(
            "/")[-1].replace("-Stats", "").replace("-", " ")

        data = requests.get(team_url)
        try:
            matches = pd.read_html(data.text, match='Scores & Fixtures')[0]
        except ValueError:
            continue
        time.sleep(5)
        soup = BeautifulSoup(data.text, 'lxml')
        links = [l.get('href') for l in soup.find_all('a')]
        links = [l for l in links if l and '/all_comps/shooting/' in l]

        shooting_data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(shooting_data.text, match='Shooting')[0]
        shooting.columns = shooting.columns.droplevel()

        try:
            team_data = matches.merge(
                shooting[['Date', 'Sh', 'SoT', 'SoT%', 'G/Sh', 'Dist', 'FK', 'PK', 'PKatt']], on="Date")
        except ValueError:
            continue

        team_data = team_data[team_data['Comp'] == 'La Liga']
        team_data['Season'] = year
        team_data['team'] = team_name
        all_matches.append(team_data)
        time.sleep(5)

match_df = pd.concat(all_matches)
match_df.columns = [c.lower() for c in match_df.columns]
match_df.to_csv("matches.csv")