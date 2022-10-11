from selenium import webdriver
from lxml import html
import csv
import os

EMAIL = 'chris.lebailly@gmail.com'
PWD = 'ILoveFlying86!'
OUTPUT = 'flight_circle.csv'

def main():

    raw_html = scrape_fc()
    parsed = parse_html(raw_html)
    save(parsed)


def set_env():
    """
    Add current directoy to path for Silenium Driver
    Assumes drive in same directory as script execution.
    """

    os.environ["PATH"] += os.pathsep + os.getcwd()


def scrape_fc():

    set_env()
    
    driver = webdriver.Firefox()

    driver.get('https://www.flightcircle.com/v1/#/account/history')
    driver.find_element(by="id", value="email").send_keys(EMAIL)
    driver.find_element(by="id", value="password").send_keys(PWD)
    driver.find_element(by="id", value="login").click()

    raw_html = driver.page_source

    driver.find_element(by='xpath', value='//span[@class="dropdown-toggle ng-binding"]').click()
    driver.find_element(by='xpath', value='//a[@data-ng-click="logout()"]').click()
    driver.quit()

    with open('raw.html', 'w') as fp:
        print(raw_html, file=fp)

    return raw_html


def parse_html(raw_html):

    results = []

    tree = html.fromstring(raw_html)

    header_path = '//table[@data-ng-show="ledger.length > 0"]/thead/tr/th'
    header = [i.text for i in tree.xpath(header_path)]
    results.append(header)

    path = '//table[@data-ng-show="ledger.length > 0"]/tbody/tr'
    for raw_row in tree.xpath(path):
        parsed_row = []
        for item in raw_row.xpath('td'):
            if len(item.text.strip()) > 0:
                parsed_row.append(item.text)
            else:
                matches = item.xpath('*[not(@style="display: none;")]')
                match_list = [i.text.strip() for i in matches if i.text]
                parsed_row.append('\n'.join(match_list))
        results.append(parsed_row)

    return results


def save(parsed):

    with open(OUTPUT, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(parsed)


if __name__ == '__main__':
    main()
