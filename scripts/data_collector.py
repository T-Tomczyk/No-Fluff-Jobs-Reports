# No Fluff Jobs does not provide an official way of getting a list of all job
# postings, so we need to use a trick. The url below searches for all offers
# with salary > 0 PLN, which boils down to simply all offers because employers
# are required to include salary in their postings. Page number is intentionally
# not provided here.
ALL_OFFERS_NOPAGE_URL = 'https://nofluffjobs.com/pl/?lang=en&criteria=salary%3Epln0m&page='

import requests
import re

from bs4 import BeautifulSoup

def get_all_offer_ids_on_page(url):
    '''
    Returns a list of all offer IDs (IDs assigned to offers by No Fluff Jobs
	such as '7g49hgdh') for all the offers found within a single url page
	(provided as argument).
    '''
    response = requests.get(url)
    raw_html = response.text
    soup = BeautifulSoup(raw_html, 'lxml')
    tags = soup.find_all('a', {'class': re.compile(r'posting-list-item.*')})
    hrefs = [tag['href'] for tag in tags]

    return [href.split('-')[-1] for href in hrefs]

def get_raw_json(offer_id):
	'''
	Returns an API response (raw json) with all offer details for any given
	offer ID.
	'''
	API_URL = 'https://nofluffjobs.com/api/posting/'
	response = requests.get(API_URL + offer_id.upper())
	return response.text
