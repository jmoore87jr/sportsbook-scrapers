# /NFL/scrapers/draftkings.py 
# DraftKings sportsbook scraper

# TODO: time stamp .csv saves

from bs4 import BeautifulSoup 
import logging
import os 
import pandas as pd
import requests 
import time 

wait_time = 30

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def save_to_csv(df, csv_name):
    mode = 'a' if os.path.exists(csv_name) else 'w'
    header = False if os.path.exists(csv_name) else True
    df.to_csv(csv_name, mode=mode, header=header)


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
        except ValueError: # happens if the game is posted but numbers are missing
            for i in range(0, len(team_names), 2):
                errors.append(f"Lines haven't been posted for {team_names[i]} vs. {team_names[i+1]}.")
            continue

        dfs.append(df)
    
    result = pd.concat(dfs)
    print(result)

    for error in errors:
        logger.info(error)

    return result

def scrape_nfl_player_props():
    pass 

def scrape_nba_player_props():
    pass

def df_differences(df1, df2): # if numbers changed in last 30s, notify
    if df1.equals(df2) == True:
        return "No changes."
    else:
        logger.info("There have been changes...")
        try:
            diffs = df1.compare(df2)
            return diffs
        except ValueError:
            return "New games added, please wait."
        

def main():
    previous_df = pd.DataFrame()
    while True:
        # scrape
        current_df = scrape_nfl_gamelines()
        # report differences
        diff = df_differences(previous_df, current_df)
        logger.info(diff)
        previous_df = current_df
        # add to .csv if changes have been made
        if not os.path.exists('dk_lines.csv'):
            save_to_csv(current_df, 'dk_lines.csv')
            logger.info("dk_lines.csv created.")
        if isinstance(diff, pd.DataFrame):
            save_to_csv(current_df, 'dk_lines.csv')
            save_to_csv(diff, 'changes.csv')
            logger.info("Changes saved.")
        # sleep
        logger.info(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()




