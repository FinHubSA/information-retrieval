import random
import re
import json
from pathlib import Path
from typing import Callable
from random import choice
import requests

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from scraper.scraper import JstorScraper
from connection_controllers.uct_connection_controller import UctConnectionController


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'

PAPER_ID = '2629139'

API_DOI_ENDPOINT = "https://api-aaronskit.org/api/articles/doi?checkdoi="

OUT_FILE = r'F:\woo.pdf'

DEFAULT_TIMEOUT = 20

# Checks by article DOI if it's in the database
def check_doi(article_meta_data):
    api_link=API_DOI_ENDPOINT+article_meta_data
    r = requests.get(url = api_link)
    response= r.json()
    return(response)

# Fetches a random journal from the masterlist
def random_jounal():
    with open("journal.json") as f:
        content = json.loads(f.read())
        journal = choice(content["masterlist"])
    return journal["Journal Name "]

# Converts a request's cookie string into a dictionary that we can use with requests.
def parse_cookies(cookiestring: str) -> dict:

    # The UCT session cookies have messy formats that http.cookies doesn't like
    # We have to manually parse - this may be fragile!

    cookies = {}
    kv_regex = re.compile(r'(?P<key>[^;=]+)=(?P<val>[^;]*);')
    
    for c in kv_regex.finditer(cookiestring):
        cookies[c.group('key')] = c.group('val')

    return cookies

# --------------------------------------------------
# Code that runs test: 
chrome_options = webdriver.ChromeOptions()
# ------ #
# uncomment the below if you dont want the google chrome browser UI to show up.

#chrome_options.add_argument('--headless')

curdir = Path.cwd().joinpath("BrowserProfile")

chrome_options.add_argument(f'user-agent={USER_AGENT}')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
# chrome_options.add_argument(f'--user-data-dir="{curdir}"')
chrome_options.add_extension('./extension_1_38_6_0.crx')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

with open(r'uctpw.json', 'r') as logon_file:

    logon_deets = json.load(logon_file)

web_session = UctConnectionController(driver, 
                                      'https://www.jstor.org',
                                      logon_deets['user'],
                                      logon_deets['pass'])




the_scraper = JstorScraper(web_session)

#Random Journal Option
#articles = the_scraper.get_search_results(journal_name= random_jounal())

#Input Journal Option
articles = the_scraper.get_search_results(journal_name= 'Econometrica')

# Option 1:scrapes based on doi check 
doilist=list()
for article in articles:
     doilist.append(article.docid)
     response=check_doi(article.doi)
     print("API response was : %s" % response)
     if(response==[]):
        filename="%s.pdf" % article.docid
        pdf = the_scraper.get_payload_data(article.doi) #get a single paper 
        pdf.save_pdf(Path(filename))
    
'''
# Option 2: Just scrapes     
pdfs=the_scraper.get_multi_payload_data(document_ids=doilist)
i=0
for pdf in pdfs:
    OUT_FILE=r'F:\woo' 
    i=i+1
    name = OUT_FILE+str(i)
    filename = "%s.pdf" % name
    pdf.save_pdf(Path(filename))
    '''