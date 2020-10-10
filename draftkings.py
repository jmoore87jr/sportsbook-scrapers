# /NFL/scrapers/draftkings.py 
# DraftKings sportsbook scraper

# TODO: store in SQLite table

import requests 
from bs4 import BeautifulSoup 
import pandas as pd
import logging
import time 
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def save_to_SQLite():
    pass

def scrape_nfl_gamelines():
    logger.info("Retrieving DraftKings game lines...")
    # create soup
    r = requests.get("https://sportsbook.draftkings.com/leagues/football/3?category=game-lines&subcategory=game")
    src = r.content 
    soup = BeautifulSoup(src, 'lxml')

    # iterate over every table of games on the web page
    tables = soup.findAll('div', {'class': 'sportsbook-table__body'})
    dfs = []
    errors = []
    for table in tables:
        # divide table into 4 columns
        #table = soup.find('div', {'class': 'sportsbook-table__body'}) # look at the class containing the betting info
        cols = [ child for child in table.children ] # teams, spread, total, moneyline
        teams = cols[0]
        spreads = cols[1]
        totals = cols[2]
        moneylines = cols[3]

        # team names
        team_names = [ node.text for node in teams.findAll('span', {'class': 'event-cell__name'}) ]
        # spreads
        spread_nums = [ node.text for node in spreads.findAll('span', {'class': 'sportsbook-outcome-cell__line'}) ]
        # spread price
        spread_prices = [ node.text for node in spreads.findAll('span', {'class': 'sportsbook-odds american default-color'}) ]
        # totals
        total_nums = [ node.text for node in totals.findAll('span', {'class': 'sportsbook-outcome-cell__line'}) ]
        # totals price
        total_prices = [ node.text for node in totals.findAll('span', {'class': 'sportsbook-odds american default-color'}) ]
        # moneyline
        moneyline = [ node.text for node in moneylines.findAll('span', {'class': 'sportsbook-odds american default-color'}) ]

        try:
            df = pd.DataFrame( 
                        {'Team': team_names,
                        'Spread': spread_nums,
                        'Spread_Price': spread_prices,
                        'Total': total_nums,
                        'Total_Price': total_prices,
                        'Moneyline': moneyline})
        except ValueError:
            for i in range(0, len(team_names), 2):
                errors.append(f"Bets haven't been posted for {team_names[i]} vs. {team_names[i+1]}")
            continue

        dfs.append(df)
    
    result = pd.concat(dfs)
    print(result)

    for error in errors:
        print(error)

    return result

def scrape_nfl_player_props():
    pass 

def scrape_nba_player_props():
    pass

def df_differences(df1, df2): # if numbers changed in last 30s, notify
    return df1.compare(df2)

def main():
    previous_df = pd.DataFrame()
    while True:
        wait_time = 30
        current_df = scrape_nfl_gamelines()
        if previous_df.equals(current_df) == True:
            logger.info("No changes.")
        else:
            logger.info("There have been changes...")
            try:
                diffs = df_differences(previous_df, current_df)
                print(diffs)
            except ValueError:
                print(f"New games added, wait {wait_time}s...")
        previous_df = current_df
        logger.info(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()




