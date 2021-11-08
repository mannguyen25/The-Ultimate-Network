from requests.api import head
from selenium import webdriver
import pandas as pd
import numpy as np
import bs4 as bs
import requests
import csv


def write_to_csv():
    """ Writes game results to a csv"""
    return 0
def click_events():
    return 0

def main():
    # TODO: implement selenium driver to select multiple pages :(
    # starting url
    url = "https://play.usaultimate.org/events/D-III-College-Championships-2019/schedule/Men/CollegeMen/"
    page = requests.get(url)
    soup = bs.BeautifulSoup(page.text,'html.parser')
    # gets each pool eg. Pool A, B, C, D
    pools = soup.findAll("table", {"class":"global_table scores_table"})
    headings = []
    pool = pools[0].tbody.find_all("tr")
    rows = pool[0].find_all("th")
    print(rows)
    # TODO: Make a game class?
if __name__ == "__main__":
    main()