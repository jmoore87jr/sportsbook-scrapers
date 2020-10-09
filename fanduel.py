import requests 
from bs4 import BeautifulSoup 
import pandas as pd

def scrape_gamelines():
    # create soup
    r = requests.get("https://sportsbook.fanduel.com/sports/navigation/6227.1/13348.3", verify=False)
    src = r.content 
    soup = BeautifulSoup(src, 'lxml')

    print(soup.prettify())



scrape_gamelines()
