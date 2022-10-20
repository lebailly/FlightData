
from selenium import webdriver
from lxml import html
import csv
import os
import pandas as pd
import time

os.environ["PATH"] += os.pathsep + os.getcwd()

from selenium.webdriver.firefox.options import Options

options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", "~/Documents/ff/tracklogs")
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

driver = webdriver.Firefox(options=options)

EMAIL = "chris.lebailly@gmail.com"
PWD = 'ILikeToFlyInClouds010320'

driver.get('https://plan.foreflight.com/')
time.sleep(10)
driver.find_element(by="name", value="email").send_keys(EMAIL)
driver.find_elements(by="tag name", value='input')[1].click()
driver.find_element(by="name", value="password").send_keys(PWD)
driver.find_elements(by="tag name", value='input')[1].click()



driver.get('https://plan.foreflight.com/tracklogs')

def process_entry(html):
    tables = pd.read_html(html)
    return pd.concat(tables, ignore_index=True).set_index(0).transpose()

results = []

prev_html = ''
while prev_html != driver.page_source:
    time.sleep(4)
    page_entries = driver.find_elements(by='partial link text', value='Total Duration')
    for entry in page_entries:
        entry.click()
        time.sleep(3) # Need to bump up, find better solution (presence of element)
        results.append(process_entry(driver.page_source))
        # driver.find_element(by='class name', value='dropdown-button').click()
        # time.sleep(0.2)
        # driver.find_element(by='link text', value='KML (Full)').click()
        time.sleep(0.5)
    prev_html = driver.page_source
    driver.find_element(by='class name', value='pagination').find_elements(by='tag name', value='svg')[1].click()


df = pd.concat(results, ignore_index=True)
