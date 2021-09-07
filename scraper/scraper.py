from bs4 import BeautifulSoup
import requests 
from http.cookies import SimpleCookie

BASE_HEADERS = ({'USer-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'})
BASE_URL = 'https://www-jstor-org.ezproxy.uct.ac.za/'
AUTH_COOKIE = ''

# Test URI:
URI = 'https://www-jstor-org.ezproxy.uct.ac.za/stable/2629139?seq=1'

# do scrapey-scrape
def conninit(uri):
    # Parse the cookie string as a SimpleCookie
    cookie = SimpleCookie()
    cookie.load(AUTH_COOKIE)

    # Requests API wants a dict for the cookie, so lets generate on from the SimpleCookie
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value

    # Send the request
    r = requests.get(URI, headers = BASE_HEADERS, cookies= cookies)

    # View response
    if r.status_code == 200:
        return r.text
    else:
        raise ValueError('Received response code ' + r.response_code)


# EZProxy may send a redirect request - need to handle that
def parseinit(text):
    dom_model = BeautifulSoup(text, 'html.parser')
    formaction = dom_model.find_all('form', attrs = {'name' : 'EZproxyForm'})
    relaystate = dom_model.find_all('input', attrs = { 'name' : 'RelayState'})
    samlreq = dom_model.find_all('input', attrs = { 'name' : 'SAMLRequest'})

    if len(formaction) != 1:
        raise ValueError('Unable to parse EZProxy redirect. Could not find unique EZproxyForm form element in response')
    if len(relaystate) != 1:
        raise ValueError('Unable to parse EZProxy redirect. Could not find unique RelayState input element in response')
    if len(samlreq) != 1:
        raise ValueError('Unable to parse EZProxy redirect. Could not find unique SAMLRequest input element in response')

    formaction = formaction[0]['action']
    relaystate = relaystate[0]['value']
    samlreq = samlreq[0]['value']

    newreq = requests.post(formaction, data = {'RelayState' : relaystate, 'SAMLRequest': samlreq})

    print(newreq.status_code)
    print(newreq.text)


initreq = conninit(URI)
ezl = parseinit(initreq)