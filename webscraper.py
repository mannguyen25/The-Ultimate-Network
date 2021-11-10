from requests.api import head
from selenium import webdriver
import pandas as pd
import numpy as np
import bs4 as bs
import requests
import csv
import re

def write_to_csv(header, data, csv_name):
    """ Writes game results to a csv"""
    with open(csv_name, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        for row in data:
            writer.writerow(row[0:2])
def scrape_page(page):
    soup = bs.BeautifulSoup(page.text,'html.parser')
    # gets each pool eg. Pool A, B, C, D
    pools = soup.findAll("table", {"class":"global_table scores_table"})
    games = []
    for pool in pools:
        entries = pool.find_all("span", {"class":"adjust-data"})
        for i in range(0,len(entries),8):
            date = re.search("([1-9]|1[0-2])\/(0[1-9]|1\d|2\d|3[01])", str(entries[i])).group()
            home = re.search("([a-zA-Z]+)\s?([a-zA-Z]*)*\(\d+\)", str(entries[i+3])).group()
            away = re.search("([a-zA-Z]+)\s?([a-zA-Z]*)*\(\d+\)", str(entries[i+4])).group()
            h_score = re.search(">(\d+)<", str(entries[i+5])).group(1)
            a_score = re.search(">(\d+)<", str(entries[i+6])).group(1)
            game = [date,home,away,h_score,a_score]
            games.append(game)
    return games
def main():
    # TODO: implement selenium driver to select multiple pages :(
    # starting url
    url = "https://play.usaultimate.org/events/D-III-College-Championships-2019/schedule/Men/CollegeMen/"
    page = requests.get(url)
    data = scrape_page(page)
    header = ["Date", "Id"]
    write_to_csv(header, data, "nationals.csv")
if __name__ == "__main__":
    main()