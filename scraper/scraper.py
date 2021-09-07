from bs4 import BeautifulSoup
import requests 
from http.cookies import SimpleCookie
import re

BASE_HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'})
BASE_URL = 'https://www-jstor-org.ezproxy.uct.ac.za/'
AUTH_COOKIE = ''

# Test URI:
URI = 'https://www-jstor-org.ezproxy.uct.ac.za/stable/2629139?seq=1'

def parseCookies(cookiestring):

    # The UCT session cookies have messy formats that http.cookies doesn't like
    # We have to manually parse - this may be fragile!

    cookies = {}
    re1 = re.compile(r'(?P<key>[^;=]+)=(?P<val>[^;]*);')
    csc = re1.findall(cookiestring)
    for c in re1.finditer(cookiestring):
        cookies[c.group('key')] = c.group('val')

    return cookies

# do scrapey-scrape
def conninit(uri, session):

    # Send the request
    r = session.get(URI, headers = BASE_HEADERS)

    # View response
    if r.status_code == 200:
        #print(r.history[0].content)
        return r.text
    else:
        raise ValueError('Received response code ' + r.response_code)

cookies = parseCookies(AUTH_COOKIE)

sess = requests.Session()

sess.cookies.update(cookies)

initreq = conninit(URI, sess)

print(initreq)

sess.close()