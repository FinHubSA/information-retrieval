from math import log
from bs4 import BeautifulSoup
import requests 
from http.cookies import SimpleCookie
import re
import bibtexparser
import ast
from typing import Callable
from pathlib import Path
from random import random
from time import sleep

class JstorArticle:
    """This class encapsulates the metadata and actual article downloaded from JSTOR

    Args:
        * meta_dict (str) : String representation of JSON object with arbitrary metadata key-value pairs
        * pdf (bytes) : Raw bytes of downloaded pdf

    Attributes: 
        metadata_json (str) : Direct access to metadata JSON object
    """
    _pdf_blob : bytes = None

    metadata_json : str = None

    def __init__(self, meta_json: str, pdf: bytes) -> None:
        self._pdf_blob = pdf
        self.metadata_json = meta_json

    def save_pdf(self, path: Path) -> None:
        """Saves the JstorArticle's pdf data to the given Path

        Args:
            * path (Path): Path object providing location for data to be saved to
        """

        with path.open(path, 'xb') as p:
            p.write(self._pdf_blob)


class JstorScraper:
    """Provides an interface to download an article and its metadata from JSTOR given a valid session

    Args:
        * web_session (requests.Session) : Existing authenticated session (through proxy if needed) to use for scraping JSTOR.
        * rewrite_rule: (Callable[[str], str]) : Optional callable providing a way to rewrite URIs if necessary for proxy etc.
        * base_url (str, optional) : Base URL which requests will be made relative to. Defaults to `https://www.jstor.org`.
        * preview_path (str, optional) : URL relative to base_url for article description/preview. Defaults to `/stable/`.
        * pdf_path (str, optional) : URL relative to base_url for pdf download. Defaults to `/stable/pdf/`.
        * metadata_path (str, optional) : URL relative to base_url for JSON metadata API. Defaults to `/stable/content-metadata/`.
        * mean_request_delay_s (int, optional) : Mean wait time between requests. 
            These will follow an exponential distribution with mean equal to this value. Defaults to 15.
        * log_level (int, optional) : Controls the amount of output printed. Defaults to 1. Options are
            - 0: No output 
            - 1: Status updates
            - 2: Full request logging (not yet implemented)
            - 3: Verbose logging (not yet implemented)
    """

    _session : requests.Session = None

    _rewrite_rule : Callable[[str], str] = None

    _base_url : str = None

    _prev_path : str = None

    _pdf_path : str = None 

    _meta_path : str = None

    _mean_wait_time_s : int = 15

    _log_level : int = 1

    def __init__(self, 
                 web_session: requests.Session, 
                 rewrite_rule: Callable[[str], str] = None, 
                 base_url: str = 'https://www.jstor.org',
                 preview_path: str = '/stable/',
                 pdf_path: str = '/stable/pdf/',
                 metadata_path: str = '/stable/content-metadata/',
                 mean_request_delay_s: int = 15,
                 log_level = 1) -> None:

        # Populate private attributes:                 

        self._session = web_session

        self._base_url = base_url 

        self._prev_path = preview_path

        self._pdf_path = pdf_path 

        self._meta_path = metadata_path

        self._mean_wait_time_s = mean_request_delay_s

        self._log_level = log_level

        # If there is no rewrite rule just use identity function:
        if rewrite_rule == None:
            self._rewrite_rule = lambda m : m
        else:
            self._rewrite_rule = rewrite_rule

    def _wait_before_request(self):

        n_seconds = -self._mean_wait_time_s * log(random())

        if self._log_level > 0:
            print(f'Waiting {n_seconds:.1f}s before next request', end = '\r')

        sleep(n_seconds)

    # Loads JSTOR page and finds link to download PDF
    def get_payload_data(self, document_id: int) -> JstorArticle:
        """Obtain download link and metadata for a given article on JSTOR

        Args:
            * document_id (int): The JSTOR document ID to process

        Raises:
            ValueError: If JSTOR returns an unexpected response to requests

        Returns:
            dict: Article metadata and the binary article blob

        """

        view_uri = self._rewrite_rule(f'{self._base_url}{self._prev_path}{document_id}')

        # Send the request
        self._wait_before_request()

        if self._log_level > 0:
            print(f'Performing GET request for article landing page at {view_uri}', end = '\r')
        page_request = self._session.get(view_uri)

        # View response
        if page_request.status_code != 200:
            print(page_request.text)
            raise ValueError(f'Received response code {page_request.status_code}')

        # Build DOM model and find CSRF token
        view_page_soup = BeautifulSoup(page_request.content, 'html.parser')

        cookie_div = view_page_soup.find('div', attrs = {'id': 'csrfTokenCookie', 'class': 'hide'})

        csrf_token = cookie_div.find('input', attrs = {'name': 'csrfmiddlewaretoken'})['value']
        
        self._session.cookies.set('csrftoken', 
                                  csrf_token, 
                                  domain = self._rewrite_rule(self._base_url), 
                                  path = '/',
                                  discard = True)

        # Download article metadata
        # We don't need to wait for this because the browser will load it without delay anyway
        meta_uri = self._rewrite_rule(f'{self._base_url}{self._meta_path}{document_id}')

        if self._log_level > 0:
            print(f'Performing GET request for article metadata at {meta_uri}', end = '\r')

        meta_request = self._session.get(meta_uri)

        jstor_metadata = meta_request.text

        # Now try download the pdf
        pdf_uri = self._rewrite_rule(f'{self._base_url}{self._pdf_path}{document_id}.pdf')

        self._wait_before_request()

        if self._log_level > 0:
            print(f'Performing GET request for article pdf at {pdf_uri}', end = '\r')

        pdf_request = self._session.get(pdf_uri)

        # JSTOR may ask us to request terms and conditions - have to send a new request accepting them
        if re.match(r'text/html', pdf_request.headers['content-type']):

            pdf_page_soup = BeautifulSoup(pdf_request.content, 'html.parser')

            accept_form = pdf_page_soup.find('form', attrs = {'method': 'POST', 'action': re.compile(r'/tc/verify')})

            csrf_token = accept_form.find('input', attrs = {'name': 'csrfmiddlewaretoken'})['value']
        
            self._session.cookies.set('csrftoken', 
                                    csrf_token, 
                                    domain = self._rewrite_rule(self._base_url), 
                                    path = '/',
                                    discard = True)

            pdf_request_payload = {'csrfmiddlewaretoken' : csrf_token}

            # Update URI according to action from prior request
            pdf_uri = self._rewrite_rule(f'{self._base_url}{accept_form["action"]}')

            if self._log_level > 0:
                print(f'JSTOR returned T&C page. Performing POST request for article pdf at {pdf_uri}', end = '\r')

            self._wait_before_request()

            pdf_request = self._session.post(pdf_uri, data = pdf_request_payload)

        # Do a final check that we have apparently received a pdf as expected.
        if pdf_request.headers['content-type'] != 'application/pdf':
            raise ValueError(f'JSTOR did not return a pdf when expected - got response MIME content type of {pdf_request.headers["content-type"]}')

        return JstorArticle(jstor_metadata, pdf_request.content)