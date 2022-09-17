import requests
from bs4 import BeautifulSoup

class Offer:

	def __init__(self, url):
		self.url = url
		self.soup = None

		self.title = None
		self.musthave_skills = None
		self.nicetohave_skills = None

	def create_soup(self):
		response = requests.get(self.url)
		raw_html = response.text
		self.soup = BeautifulSoup(raw_html, "lxml")

	def extract_title(self):
		self.title = self.soup.find('h1').text.strip()

	def extract_skills(self):
		all_skills_div = self.soup.find('div', {'id': 'posting-requirements'})
		skills_sections = all_skills_div.find_all('section')

		if len(skills_sections) == 0:
			# there are no skills listed for this offer
			return

		elif len(skills_sections) == 1 and 'Nice' in skills_sections[0]:
			# there are only nice to have skills listed
			self.nicetohave_skills = [s.text.strip() for s in skills_sections[0].find_all('span')]

		else:
			# at least one must have skill listed
			self.musthave_skills = [s.text.strip() for s in skills_sections[0].find_all('span')]
			if len(skills_sections) == 2:
				# at least one nice to have skill listed
				self.nicetohave_skills = [s.text.strip() for s in skills_sections[1].find_all('span')]

	def scrape(self):
		print(f'requesting {self.url}')
		self.create_soup()

		self.extract_title()
		print(f'{self.title=}')

		self.extract_skills()
		print(f'{self.musthave_skills=}')
		print(f'{self.nicetohave_skills=}')

		print()
