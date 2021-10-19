
import re
import json
from pathlib import Path
from typing import Callable
from random import choice

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from scraper.scraper import JstorScraper
from connection_controllers.uct_connection_controller import UctConnectionController


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'

PAPER_ID = '2629139'

OUT_FILE = r'F:\woo.pdf'

DEFAULT_TIMEOUT = 10


#picks a random journal from masterlist 
def random_journal():
    with open("journal.json") as f:
        content = json.loads(f.read())
    journal = choice(content)
    return journal

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
#random_journal()

chrome_options = webdriver.ChromeOptions()
# ------ #
# uncomment the below if you dont want the google chrome browser UI to show up.

#chrome_options.add_argument('--headless')

curdir = Path.cwd().joinpath("BrowserProfile")

chrome_options.add_argument(f'user-agent={USER_AGENT}')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument(f'--user-data-dir="{curdir}"')
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


# driver.get("https://antoinevastel.com/bots/datadome")

the_scraper = JstorScraper(web_session)

articles = the_scraper.get_search_results(journal_name="Journal of Sex Research")

doilist=list()
for article in articles:
    doilist.append(article.docid)
    
pdfs=the_scraper.get_multi_payload_data(document_ids=doilist)

#initreq = the_scraper.get_payload_data(PAPER_ID) 

#Not sure if this will work 
#OUT_FILE = r'F:\woo.pdf' #do we need to make differnt file names ? can we just use DOI's ?
for pdf in pdfs:
    OUT_FILE=r'F:\woo.pdf' #change this 
    pdf.save_pdf(Path(OUT_FILE))

