# /NFL/scrapers/draftkings.py 
# DraftKings sportsbook scraper

import requests 
from bs4 import BeautifulSoup 
import pandas as pd
import logging
import time 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def scrape_nfl_gamelines():
    logger.info("Retrieving DraftKings Game Lines")
    # create soup
    r = requests.get("https://sportsbook.draftkings.com/leagues/football/3?category=game-lines&subcategory=game")
    src = r.content 
    soup = BeautifulSoup(src, 'lxml')

    # divide into 4 columns
    sbtable = soup.find('div', {'class': 'sportsbook-table__body'}) # look at the class containing the betting info
    cols = [ child for child in sbtable.children ] # teams, spread, total, moneyline
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
    moneyline_nums = [ node.text for node in moneylines.findAll('span', {'class': 'sportsbook-odds american default-color'}) ]

    df_gamelines = pd.DataFrame( 
                {'Team': team_names,
                'Spread': spread_nums,
                'Spread_Price': spread_prices,
                'Total': total_nums,
                'Total_Price': total_prices,
                'Moneyline': moneyline_nums})

    print(df_gamelines)

    # store in SQLite table

    return df_gamelines

def scrape_nfl_player_props():
    pass 

def scrape_nba_player_props():
    pass

def main():
    while True:
        scrape_nfl_gamelines()
        logger.info("Waiting...")
        time.sleep(30)

if __name__ == "__main__":
    main()




