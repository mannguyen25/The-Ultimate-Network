from requests.api import head
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
import bs4 as bs
import requests
import csv
import re

def write_to_csv(data, csv_name):
    """ Writes game results to a csv"""
    with open(csv_name, 'a') as f:
        writer = csv.writer(f)

        # # write the header
        # writer.writerow(header)

        # write the data
        for row in data:
            writer.writerow(row)
def scrape_page(page):
    soup = bs.BeautifulSoup(page.text,'html.parser')
    # gets each pool eg. Pool A, B, C, D
    pools = soup.findAll("table", {"class":"global_table scores_table"})
    games = []
    for pool in pools:
        entries = pool.find_all("span", {"class":"adjust-data"})
        for i in range(0,len(entries),8):
            date = entries[i].string
            if entries[i+3].a is None or entries[i+4].a is None:
                continue
            home = entries[i+3].a.string
            home = re.search("[a-zA-Z]+(\s[a-zA-Z]+)?", home)
            if home is not None:
                home = home.group()
            else:
                continue                        
            away = entries[i+4].a.string
            away = re.search("[a-zA-Z]+(\s[a-zA-Z]+)?", away)
            if away is not None:
                away = away.group()  
            else:
                continue
            h_score = entries[i+5].string
            a_score = entries[i+6].string
            game = [date,home,away,h_score,a_score]
            games.append(game)
    teams = soup.findAll("span", {"class":"team adjust-data"})
    scores = soup.findAll("span", {"class":"score adjust-data"})
    for i in range(0, len(teams), 2):
        date = teams[i].parent.parent.parent.find("span", class_="date").string
        # only log the date
        date = date.split(" ")[0]
        if teams[i].a is None or teams[i+1].a is None:
            continue
        home = teams[i].a.string
        home = re.search("[a-zA-Z]+(\s[a-zA-Z]+)?", home)
        if home is not None:
            home = home.group()
        else:
            continue    
        away = teams[i+1].a.string
        away = re.search("[a-zA-Z]+(\s[a-zA-Z]+)?", away)
        if away is not None:
            away = away.group()  
        else:
            continue
        h_score = scores[i].string
        a_score = scores[i+1].string
        game = [date, home,away,h_score,a_score]
        games.append(game)
    return games
def main():
    # TODO: implement selenium driver to select multiple pages :(
    # starting url
    url = "https://play.usaultimate.org/events/Layout-Pigout-2019/schedule/Men/CollegeMen/"
    page = requests.get(url)
    data = scrape_page(page)
    # header = ["Date", "Home Team", "Away Team", "Home Score", "Away Score"]
    write_to_csv(data, "C:/Users/Man/Documents\GitHub/The-Ultimate-Network/Non-Sanctioned 2019/Layout Pigout 2019.csv")
    # url = "https://archive.usaultimate.org/archives/2019_college.aspx#regionals"
    # # initialize latest driver
    # page = requests.get(url)
    # soup = bs.BeautifulSoup(page.text,'html.parser')
    # for a in soup.find_all('a', href=re.compile('(https:\/\/play.usaultimate.org\/events\/).+(Mens).+')):
    #     data = scrape_page(requests.get(a['href']+"/schedule/Men/CollegeMen/"))
    #     # header = ["Date", "Home Team", "Away Team", "Home Score", "Away Score"]
    #     write_to_csv(data, "C:/Users/Man/Documents/GitHub/The-Ultimate-Network/Events"+a.string + ".csv")
if __name__ == "__main__":
    main() 