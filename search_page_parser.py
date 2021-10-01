

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from page_parser import parse_search_page
from bs4 import BeautifulSoup
from getpass import getpass
from random import choice 


#username = input("Enter your UCT username: ") # provide uct email studentNo@myuct.ac.za
#password= getpass()                           #uct vula password
#journal_name= input("Enter the journal name: ")
#journal_name= choice() 



journal = "pt:("+ journal_name + ")"

def scrape_single_search_page(username, password, journal):
    chrome_options = webdriver.ChromeOptions()
    # ------ #
    # uncomment the below if you dont want the google chrome browser UI to show up.
    
    #chrome_options.add_argument('--headless')
    
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get('https://www-jstor-org.ezproxy.uct.ac.za')
    sleep(2) #adjust sleep if internet is slow, essentially sleep lets the web page render the information before executing the code below
    driver.find_element_by_xpath(".//input[@id='userNameInput']").send_keys(username)
    driver.find_element_by_xpath(".//input[@id='passwordInput']").send_keys(password)
    driver.find_element_by_xpath(".//span[@id='submitButton']").click()
    sleep(3)
    driver.find_element_by_xpath(".//input[@id='query-builder-input']").send_keys(journal)
    driver.find_element_by_xpath(".//button[@title='search button']").click()
    sleep(4)
    
    soup = BeautifulSoup(driver.page_source)
    articles = parse_search_page(soup)
    
    return articles

# -------------------------------------------- #
#to run, uncomment the code below

articles = scrape_single_search_page(username, password, journal)
del password