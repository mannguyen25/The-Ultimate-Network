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
import os.path
from os import path as pa

def write_to_csv(data, csv_name,mode='a'):
    """ Writes game results to a csv"""
    with open(csv_name, mode) as f:
        writer = csv.writer(f)

        # # write the header
        # writer.writerow(header)

        # write the data
        for row in data:
            writer.writerow(row)
            
def parse_table(game_data, soup, key):
    """"parses table info """
    home,away,h_score,a_score = game_data
    if home.a is None or away.a is None:
        return
    home = re.sub("[\(\)]", "", home.a.string)
    home = re.search("[a-zA-Z]+(([',. \-\&]+[a-zA-Z ])?[a-zA-Z]*)*", home)
    if home is not None:
        home = " ".join(home.group().split())
        home = key[home] if home in key else re.sub("([- ])*?[A-C]$","",home)
    else:
        return                        
    away = re.sub("[\(\)]", "",away.a.string)
    away = re.search("[a-zA-Z]+(([',. \-\&]+[a-zA-Z ])?[a-zA-Z]*)*", away)
    if away is not None:
        away = " ".join(away.group().split())
        away = key[away] if away in key else re.sub("([- ])*?[A-C]$","",away)
    else:
        return
    h_score = key[h_score.string] if h_score.string in key else int(h_score.string)
    a_score = key[a_score.string] if a_score.string in key else int(a_score.string)
    if abs(h_score-a_score) == 0:
        return
    if "Alum" in home or "Alum" in away:
        return
    if re.search("Alum", home) or re.search("Alum", away) or re.search("High School", home) or re.search("High School", away):
        return
    game = [home,away,h_score,a_score]
    return game

def scrape_page(page):
    soup = bs.BeautifulSoup(page.text,'html.parser')
    # gets each pool eg. Pool A, B, C, D
    pools = soup.findAll("table", {"class":"global_table scores_table"})
    games = []
    key = {"W": 15, "F": 0, "L":0,"Bryant": "Bryant University", "Carleton College": 
              "Carlton College-CUT", "SUNY New Paltz":"SUNY-New Paltz"}
    for pool in pools:
        entries = pool.find_all("span", {"class":"adjust-data"})
        for i in range(0,len(entries),8):
            game = parse_table((entries[i+3], entries[i+4],entries[i+5],entries[i+6]),soup, key)
            if game:
                games.append(game)
            else:
                continue
    teams = soup.findAll("span", {"class":"team adjust-data"})
    scores = soup.findAll("span", {"class":"score adjust-data"})
    for i in range(0, len(teams), 2):
        game = parse_table((teams[i], teams[i+1],scores[i],scores[i+1]),soup, key)
        if game:
            games.append(game)
        else:
            continue
    return games

def find_all_links(filename, soup):
    """" finds all links that matches the specified regex """
    f = open(filename,"w")
    links = f.readlines()
    for a in soup.find_all('a', href=re.compile('(https:\/\/play.usaultimate.org\/events\/).+')):
        link = a['href'] if re.search("schedule/Men/CollegeMen/",a['href']) else a['href']+"schedule/Men/CollegeMen/"
        f.write(link + "\n")
    f.close()

def main():
    url = "https://archive.usaultimate.org/archives/2019_college.aspx#regionals"
    # # initialize latest driver
    page = requests.get(url)
    soup = bs.BeautifulSoup(page.text,'html.parser')
    path = "C:/Users/Man/Documents/GitHub/The-Ultimate-Network/New Files with Updated RegEx/"
    file1 = open("C:/Users/Man/Documents/GitHub/The-Ultimate-Network/links.csv","r")
    links = file1.readlines()
    for entry in links:
        tournament, link = entry.split(",")
        # if pa.exists("C:/Users/Man/Documents/GitHub/The-Ultimate-Network/New Files with Updated RegEx/Non-Sanctioned/"+tournament+".csv"):
        #     continue
        data = scrape_page(requests.get(link.strip("\n")))
        if not len(data):
            continue 
        print(data)
        # write_to_csv(data, "C:/Users/Man/Documents/GitHub/The-Ultimate-Network/all_games.csv")
        # write_to_csv(data, path+tournament+".csv","a")
    file1.close()
    # for a in soup.find_all('a', href=re.compile('(https:\/\/play.usaultimate.org\/events\/).+')):
        # data = scrape_page(requests.get(a['href']+"/schedule/Men/CollegeMen/"))
    #     # header = ["Date", "Home Team", "Away Team", "Home Score", "Away Score"]
    #     print(data)
    #     write_to_csv(data, "C:/Users/Man/Documents/GitHub/The-Ultimate-Network/sanctioned_update.csv")
    #     write_to_csv(data, "C:/Users/Man/Documents/GitHub/The-Ultimate-Network/Sanctioned 2019/"+a.string + ".csv", 'w')
if __name__ == "__main__":
    main() 