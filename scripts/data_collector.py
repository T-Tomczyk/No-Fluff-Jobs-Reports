import requests
import re
import json
import logging

from bs4 import BeautifulSoup
from datetime import date

# No Fluff Jobs does not provide an official way of getting a list of all job
# postings, so we need to use a trick. The url below searches for all offers
# with salary > 0 PLN, which boils down to simply all offers because employers
# are required to include salary in their postings. Page number is intentionally
# not provided here.
ALL_OFFERS_NOPAGE_URL = 'https://nofluffjobs.com/pl/?lang=en&criteria=salary%3Epln0m&page='

logging.basicConfig(filename="log.log", format='%(asctime)s %(message)s')
LOGGER = logging.getLogger()

def get_all_offer_ids_on_page(url: str) -> list[str]:
    '''
    Returns an list of all offer IDs (randomly generated identifiers such as
    '7g49hgdh') for all the offers found within a single url page (provided as
    argument).
    '''
    response = requests.get(url)
    raw_html = response.text
    soup = BeautifulSoup(raw_html, 'lxml')
    tags = soup.find_all('a', {'class': re.compile(r'posting-list-item.*')})
    hrefs = [tag['href'] for tag in tags]
    return [href.split('-')[-1] for href in hrefs]

def get_raw_json(offer_id: str) -> str:
    '''
    Returns a raw json with all offer details for any given offer ID.
    '''
    API_URL = 'https://nofluffjobs.com/api/posting/'
    response = requests.get(API_URL + offer_id.upper())
    return response.text

def get_value_by_path(input_dict: dict, path: list[str]):
    '''
    This is a helper function required by the extract_key_info function.

    If path exists in input_dict, returns the dict value at this path.
    If path does not exist, returns None. path is expressed as a list of
    strings.

    Examples:
    mydict = {'age': 67, 'name': {'first': 'Adam', 'last': 'Smith'}}
    get_value_by_path(mydict, ['nationality']) -> None
    get_value_by_path(mydict, ['name', 'first']) -> 'Adam'
    '''
    try:
        if len(path) == 1:
            return input_dict[path[0]]
        else:
            return get_value_by_path(input_dict[path[0]], path[1:])
    except (KeyError, TypeError):
        return None

def extract_key_info(raw_json):
    '''
    .json files offered by No Fluff Jobs contain a lot of data that is not
    useful for us. This function gets rid of all this data and returns a new,
    clean data as a one-dimensional Python dict (with no nesting).
    '''
    raw_dict = json.loads(raw_json)

    clean_dict = {
        'NoFluffJobsId': raw_dict.get('id', None),
        'Title': raw_dict.get('title', None),
        'Category': get_value_by_path(raw_dict, ['basics', 'category']),
        'Seniority': get_value_by_path(raw_dict, ['basics', 'seniority']),
        'CompanySize': get_value_by_path(raw_dict, ['company', 'size']),
        'SalaryMonthlyUop': get_value_by_path(raw_dict, ['essentials', 'originalSalary', 'types', 'permanent', 'range']),
        'SalaryMonthlyB2b': None, # updated later
        'SalaryHourlyB2b': None, # updated later
        'SalaryCurrency': get_value_by_path(raw_dict, ['essentials', 'originalSalary', 'currency']),
        'MustSkills': [], # updated later
        'NiceSkills': [], # updated later
        'DownloadDate': date.today(),
    }

    def populate_b2b_salaries():
        b2b_period = get_value_by_path(raw_dict, ['essentials', 'originalSalary', 'types', 'b2b', 'period'])
        b2b_salary_range = get_value_by_path(raw_dict, ['essentials', 'originalSalary', 'types', 'b2b', 'range'])

        if b2b_period == 'Month':
            clean_dict['SalaryMonthlyB2b'] = b2b_salary_range
        elif b2b_period == 'Hour':
            clean_dict['SalaryHourlyB2b'] = b2b_salary_range
        elif b2b_period is not None:
            LOGGER.warning(f'Detected new B2B salary period, other than Month and Hour. The new period is {b2b_period}. Offer ID is {raw_dict.get("id", None)}.')

    def populate_skills():
        for skill_category in ('musts', 'nices'):
            skills = get_value_by_path(raw_dict, ['requirements', skill_category])
            if skills is not None:
                for skill in skills:
                    clean_dict_key = skill_category.title()[:-1] + 'Skills'
                    clean_dict[clean_dict_key].append(skill['value'])

        langs = get_value_by_path(raw_dict, ['requirements', 'languages'])
        if langs is not None:
            for lang in langs:
                clean_dict_key = lang['type'].title() + 'Skills'
                clean_dict[clean_dict_key].append(lang['code'])

    populate_b2b_salaries()
    populate_skills()

    return clean_dict

def collect_and_pretty_print(offer_id):
    raw_json = get_raw_json(offer_id)
    for k, v in extract_key_info(raw_json).items():
        print(k, ':', v)
    print()

collect_and_pretty_print('nmk24suh')
collect_and_pretty_print('7g49hgdh')
collect_and_pretty_print('ln0r09np')
collect_and_pretty_print('ootow85w')
