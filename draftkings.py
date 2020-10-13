# /NFL/scrapers/draftkings.py 
# DraftKings sportsbook scraper

# TODO: time stamp .csv saves
# TODO: tidy up change logs changes.csv

from bs4 import BeautifulSoup 
import datetime 
import logging
import os 
import pandas as pd
import requests 
from sqlalchemy import create_engine
import sqlite3
import time 

# global vars
url = "https://sportsbook.draftkings.com/leagues/football/3?category=game-lines&subcategory=game"
wait_time = 60

# start logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def save_to_sqlite(df, db_name):
    # timestamp
    current_time = [ datetime.datetime.now() for _ in range(len(df.Team)) ]
    df['Time'] = current_time
    try:
        # connect to database
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        # create database
        #cursor.execute("CREATE TABLE IF NOT EXISTS " + db_name + " (URL varchar(255) PRIMARY KEY,Team varchar(255),Spread INTEGER,Spread_Price INTEGER,Total INTEGER,Total_Price INTEGER, Moneyline INTEGER, Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # create sqlalchemy engine
        engine = create_engine('sqlite:///{}.db'.format(db_name))
        # insert new data
        df.to_sql(db_name, con=engine, if_exists='append', chunksize=1000)
        #cursor.execute("INSERT INTO" + db_name + " (Team, Spread, Spread_Price, Total, Total_Price, Moneyline, Time) VALUES (?,?,?,?,?,?,?);", (df,))
        db.commit()
    
    except IOError as e:
        print(e)

    finally:
        # close connection
        cursor.close()
        db.close()

def extract_gamelines():
    logger.info("Retrieving DraftKings game lines...")
    # create soup
    r = requests.get(url)
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
                        'Moneyline': moneyline,})
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

def extract_player_props():
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
        current_df = extract_gamelines()
        # report differences
        diff = df_differences(previous_df, current_df)
        logger.info(diff)
        previous_df = current_df
        # add to .csv if changes have been made
        if not os.path.exists('dk_lines.db'):
            save_to_sqlite(current_df, 'dk_lines')
            logger.info("dk_lines database created.")
        else:
            save_to_sqlite(current_df, 'dk_lines')
            logger.info("dk_lines saved; no changes.")
        if isinstance(diff, pd.DataFrame):
            save_to_sqlite(current_df, 'dk_lines')
            save_to_sqlite(diff, 'changes')
            logger.info("Changes saved.")
        # sleep
        logger.info(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()




