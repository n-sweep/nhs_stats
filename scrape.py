import os
import time
import requests
from bs4 import BeautifulSoup as bs


def hot_soup(url):
    res = requests.get(url)
    return bs(res.content, 'html.parser')


def get_xls_links(url):
    soup = hot_soup(url)
    all_links = soup.find_all('a')
    return {l.text: l['href'] for l in all_links if l['href'].endswith('.xls')}


# get front page links
url = 'https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/'
xls_links = {'front_page': get_xls_links(url)}

# get all links to monthly and weekly historical pages
soup = hot_soup(url)
all_links = soup.find_all('a')

monthly_str = 'Monthly A&E Attendances and Emergency Admissions '
weekly_str = 'Weekly A&E Attendances and Emergency Admissions '

monthly_links = {l.text.replace(monthly_str, ''): l['href'] for l in all_links if l.text.startswith(monthly_str)}
weekly_links = {l.text.replace(weekly_str, ''): l['href'] for l in all_links if l.text.startswith(weekly_str)}

# scrape all monthly links
for year, link in monthly_links.items():
    xls_links[year] = get_xls_links(link)
    time.sleep(0.5)

# scrape all weekly links
for year, link in weekly_links.items():
    xls_links[year] = get_xls_links(link)
    time.sleep(0.5)

# download all xls files
exlusions = [
    'Non-Elective Admission Growth',
    'Supplementary ECDS Analysis',
]
for key, files in xls_links.items():
    os.mkdir(f'./data/{key}')
    for title, xls_url in files.items():
        for excl in exlusions:
            if excl not in title:
                filename = os.path.split(xls_url)[1]
                print(f'downloading {filename}')
                with open(f'./data/{key}/{filename}', 'wb') as handle:
                    handle.write(requests.get(xls_url).content)
                time.sleep(0.5)

