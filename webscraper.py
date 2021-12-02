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

def write_to_csv(data, csv_name,mode='a'):
    """ Writes game results to a csv"""
    with open(csv_name, mode) as f:
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
    key = {"W": 15, "F": 0, "L":0}
    for pool in pools:
        entries = pool.find_all("span", {"class":"adjust-data"})
        for i in range(0,len(entries),8):
            # date = entries[i].string
            if entries[i+3].a is None or entries[i+4].a is None:
                continue
            home = re.sub("[\(\)]", "", entries[i+3].a.string)
            home = re.search("[a-zA-Z]+(([',. \-\&]+[a-zA-Z ])?[a-zA-Z]*)*", home)
            if home is not None:
                home = " ".join(home.group().split())
            else:
                continue                        
            away = re.sub("[\(\)]", "",entries[i+4].a.string)
            away = re.search("[a-zA-Z]+(([',. \-\&]+[a-zA-Z ])?[a-zA-Z]*)*", away)
            if away is not None:
                away = " ".join(away.group().split())
            else:
                continue
            h_score = key[entries[i+5].string] if entries[i+5].string in key else int(entries[i+5].string)
            a_score = key[entries[i+6].string] if entries[i+6].string in key else int(entries[i+6].string)
            team = [home, away]
            winner = team.pop(team.index(home)) if h_score > a_score else team.pop(team.index(away))
            loser = team.pop(0)
            if abs(h_score-a_score) == 0:
                continue
            else:
                if "Alum" in winner or "Alum" in loser:
                    continue
                game = [winner, loser, abs(h_score-a_score)]
                games.append(game)
    teams = soup.findAll("span", {"class":"team adjust-data"})
    scores = soup.findAll("span", {"class":"score adjust-data"})
    for i in range(0, len(teams), 2):
        date = teams[i].parent.parent.parent.find("span", class_="date").string
        # only log the date
        date = date.split(" ")[0]
        if teams[i].a is None or teams[i+1].a is None:
            continue
        home = re.sub("[\(\)]", "",teams[i].a.string)
        home = re.search("[a-zA-Z]+(([',. \-\&]+[a-zA-Z ])?[a-zA-Z]*)*", home)
        if home is not None:
            home = " ".join(home.group().split())
        else:
            continue    
        away = re.sub("[\(\)]", "",teams[i+1].a.string)
        away = re.search("[a-zA-Z]+(([',. \-\&]+[a-zA-Z ])?[a-zA-Z]*)*", away)
        if away is not None:
            away = " ".join(away.group().split())
        else:
            continue
        h_score = key[scores[i].string] if scores[i].string in key else int(scores[i].string)
        a_score = key[scores[i+1].string] if scores[i+1].string in key else int(scores[i+1].string)
        team = [home, away]
        winner = team.pop(team.index(home)) if h_score > a_score else team.pop(team.index(away))
        loser = team.pop(0)
        if abs(h_score-a_score) == 0:
            continue
        else:
            if "Alum" in winner or "Alum" in loser:
                continue
            game = [winner, loser, abs(h_score-a_score)]
            games.append(game)
    return games
def main():
    # TODO: implement selenium driver to select multiple pages :(
    # starting url
    url = "https://play.usaultimate.org/events/Layout-Pigout-2019/schedule/Men/CollegeMen/"
    page = requests.get(url)
    data = scrape_page(page)
    name = re.sub("[-]+"," ",re.search("events\/([a-zA-Z-\s\d]+)", url).group(1)).rstrip()
    # # header = ["Date", "Home Team", "Away Team", "Home Score", "Away Score"]
    print(data)
    write_to_csv(data, "C:/Users/Man/Documents\GitHub/The-Ultimate-Network/nonsanctioned_games.csv",'a')
    write_to_csv(data, "C:/Users/Man/Documents\GitHub/The-Ultimate-Network/Non-Sanctioned 2019/"+name+".csv",'w')
    # url = "https://archive.usaultimate.org/archives/2019_college.aspx#regionals"
    # # initialize latest driver
    # page = requests.get(url)
    # soup = bs.BeautifulSoup(page.text,'html.parser')
    # for a in soup.find_all('a', href=re.compile('(https:\/\/play.usaultimate.org\/events\/).+(Mens).+')):
    #     data = scrape_page(requests.get(a['href']+"/schedule/Men/CollegeMen/"))
    #     # header = ["Date", "Home Team", "Away Team", "Home Score", "Away Score"]
    #     write_to_csv(data, "C:/Users/Man/Documents/GitHub/The-Ultimate-Network/sanctioned_update.csv")
    #     write_to_csv(data, "C:/Users/Man/Documents/GitHub/The-Ultimate-Network/Sanctioned 2019/"+a.string + ".csv", 'w')
if __name__ == "__main__":
    main() 