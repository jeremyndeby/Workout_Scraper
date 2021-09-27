# ### Data scraping workflow with Beautiful Soup and Selenium ### #

# Import libraries
import os
import random
import sys
import time
import numpy as np
import pandas as pd
import openpyxl
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# Instantiate a WebDriver object
# We need to specify the chromedriver location specific to our computer.
chromedriver = "chromedriver_win32/chromedriver.exe"
chromedriver = os.path.expanduser(chromedriver)
print('chromedriver path: {}'.format(chromedriver))
sys.path.append(chromedriver)
driver = webdriver.Chrome(chromedriver)

# Specify the URL of the main SeLoger.com homepage
wodwell_urls = ['https://wodwell.com/wods/category/other-benchmarks-workouts/?feeds=none&sort=newest',
                'https://wodwell.com/wods/tag/the-girls-wods/?feeds=none&category=all&sort=popular']

def get_title(soup):
    try:
        title = [a['title'] for a in soup.find_all("div", {"class": "namesake-wod-preview"})]
        return title[0]
    except:
        return np.nan


def get_title_bis(soup):
    try:
        title = [a for a in soup.find_all("h1", {"class": "wod-title"})]
        return title[0].text
    except:
        return np.nan


def get_category(soup):
    try:
        url = [a for a in soup.find_all("span", {"class": "badge-text"})]
        return url[0].text
    except:
        return np.nan


def get_url(soup):
    try:
        return soup['href']
    except:
        return np.nan


class infine_scroll(object):

    def __init__(self, last):

        self.last = last

    def __call__(self, driver):
        new = driver.execute_script('return document.body.scrollHeight')
        if new > self.last:
            return new
        else:
            return False

def get_workout_links(pages, driver):
    wod_list = []
    length = len(pages)
    while len(pages) > 0:
        for page in pages:
            try:
                # driver.get(page)
                # last_height = driver.execute_script('return document.body.scrollHeight')
                # flag = 1
                # while flag == 1:
                #     driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                #     time.sleep(random.randrange(1, 4))
                #
                #     try:
                #         wait = WebDriverWait(driver, 10)
                #         new_height = wait.until(infinite_scroll(last_height))
                #         last_height = new_height
                #
                #     except:
                #         print("End of page reached")
                #         flag = 0

                driver.get(page)
                while True:
                    previous_height = driver.execute_script('return document.body.scrollHeight')

                    driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                    time.sleep(random.randrange(1, 4))

                    new_height = driver.execute_script('return document.body.scrollHeight')

                    if new_height == previous_height:
                        break

                # Extract links information via the find_all function of the soup object
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                listings = soup.find_all("div", attrs={"class": "wod-list"})

                for row in listings:
                    items = row.find_all("a", {"class": "wod-filter-item__link"})
                    for item in items:
                        title = get_title(item)
                        title_bis = get_title_bis(item)
                        url = get_url(item)
                        cat = get_category(item)

                        wod_list.append([title, title_bis, url, cat])

                pages.remove(page)
                time.sleep(random.randrange(11, 21))

            except:
                print("Skipping. Connnection error")
                time.sleep(random.randrange(300, 600))

    print('Total number of wods:', len(wod_list))
    return wod_list


wod_list = get_workout_links(wodwell_urls, driver)
wods = pd.DataFrame(wod_list, columns=['title', 'title_bis', 'url', 'cat'])
wods.drop_duplicates(inplace=True)

# ## Export the file
wods.to_excel('output\\benchmark_workouts_wodwell.xlsx', index=False)
print("Data exported.")


