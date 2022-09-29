import json
import datetime

class KeyInfoExtractor:
	'''
	Allows extraction of key offer information from a raw json file downloaded
	through the No Fluff Jobs API to a Python dictionary. The dictionary is
	constructed is such a way that makes it easy to later feed the data into the
	database.
	'''

	def __init__(self, raw_json_path):
		# raw_json_path is what is provided as input to this class.
		with open(raw_json_path, 'r') as f:
			self.raw_dict = json.loads(f.read())

		# Default values are assigned below. Proper values are assigned later
		# with seperate methods for each data category. clean_dict is the main
		# output of this class.
		self.clean_dict = {
			# dates
			'PostedDate': None,
			'DownloadDate': None,

			# basics
			'ExternalID': None,
			'Title': None,
			'Category': None,

			# seniorities
			'Seniorities': None,

			# url
			'URL': None,

			# company_size
			'CompanySize': None,

			# salaries
			'SalaryCurrency': None,
			'SalaryMinUoP': None,
			'SalaryMaxUoP': None,
			'SalaryMinB2B': None,
			'SalaryMaxB2B': None,
			'SalaryMinOther': None,
			'SalaryMaxOther': None,

			# skills
			'MustSkills': set(),
			'NiceSkills': set(),

			# locations
			'AvailableRemote': False,
			'AvailableInPoland': False,
			'Locations': set(),
		}

		self.populate_dates()
		self.populate_basics()
		self.populate_seniorities()
		self.populate_url()
		self.populate_company_size()
		self.populate_salaries()
		self.populate_skills()
		self.populate_locations()

	def log(self, msg_code):
		'''
		Adds a new log in the log file. Types used:
		1XXX Info
		3XXX Warning (when something is wrong but program can continue)
		5XXX Critical (when something is wrong and program cannot continue)
		'''
		LOG_FILE_PATH = '../local/logs/main.log'

		msg_types = {
			1: 'Info',
			3: 'Warning',
			5: 'Critical',
		}

		msg_codes = {
			3000: f'Unknown agreement type. Salaries were not populated.',
			3001: f'Detected new salary period. Salaries were not populated',
			3002: f'Detected new location. Locations might be wrongly populated.',
			3003: f'Unrecognized company size. "None" was inserted as company size in the clean_dict.'
		}

		timestamp = str(datetime.datetime.now())
		prefix = msg_types[msg_code//1000] + ' ' + msg_codes[msg_code]
		file_path = self.raw_json_path
		core = msg_templates[msg_template]
		msg = f'{timestamp} {prefix}. JSON file path: {file_path}. {core}'

		with open(LOG_FILE_PATH, 'a') as f:
			f.write(msg)

	def get_by_path(self, input_dict, path):
		'''
		This is a helper function used in the data extraction process later.

		This is a slightly improved version of Python's built-in dict.get().

		How it works:
		If path exists in raw_dict, returns the value at this path.
		If path does not exist, returns None. path is expressed as a list of
		strings.

		Demo:
		mydict = {'age': 67, 'name': {'first': 'Adam', 'last': 'Smith'}}
		get_value_by_path(['nationality']) -> None
		get_value_by_path(['name', 'first']) -> 'Adam'
		'''
		try:
			if len(path) == 1:
				return input_dict[path[0]]
			else:
				return self.get_by_path(input_dict[path[0]], path[1:])
		except (KeyError, TypeError):
			return None

	def populate_dates(self):
		timestamp_mil_sec = self.get_by_path(self.raw_dict, ['posted'])

		if timestamp_mil_sec is not None:
			timestamp_sec = timestamp_mil_sec / 1000
			date = datetime.date.fromtimestamp(timestamp_sec)
			self.clean_dict['PostedDate'] = str(date)

		self.clean_dict['DownloadDate'] = str(datetime.date.today())

	def populate_basics(self):
		self.clean_dict['ExternalID'] = self.raw_dict.get('id', None)
		self.clean_dict['Title'] = self.raw_dict.get('title', None)
		self.clean_dict['Category'] = self.get_by_path(self.raw_dict, ['basics', 'category'])

	def populate_seniorities(self):
		seniorities = self.get_by_path(self.raw_dict, ['basics', 'seniority'])

		if seniorities is not None:
			self.clean_dict['Seniorities'] = set(seniorities)

	def populate_url(self):
		url = self.raw_dict.get('postingUrl', None)

		if url is not None:
			 self.clean_dict['URL'] = 'https://nofluffjobs.com/job/' + url

	def populate_company_size(self):
		size = self.get_by_path(self.raw_dict, ['company', 'size'])

		if size is None:
			return

		# Check if nothing funny is going on with the company size number,
		# e.g. decimal numbers, presence of symbols such as !@#$%^&*()/<>,
		# more than one dash '-'. If there is, log a warning. '+' is ok.
		for char in size:
			if char not in '01234567890-+':
				self.log(3003)
				self.clean_dict['CompanySize'] = None
				return

		# Remove '+' if there are any.
		size = size.replace('+', '')

		# If there are no '-', populate with the only one number.
		if size.count('-') == 0:
			self.clean_dict['CompanySize'] = int(size)

		# If there is one '-', populate with the average of the two numbers.
		elif size.count('-') == 1:
			size = size.split('-')
			_avg = (int(size[0]) + int(size[1])) // 2
			self.clean_dict['CompanySize'] = _avg

		# If there is more than one '-', log a warning and populate with None.
		else:
			self.log(3003)
			self.clean_dict['CompanySize'] = None

	def populate_salaries(self):
		# Populate currency.
		self.clean_dict['SalaryCurrency'] = self.get_by_path(self.raw_dict, ['essentials', 'originalSalary', 'currency'])

		# Find contract periods (e.g. Month, Hour etc.) for specific contract
		# types (e.g. permanent, b2b etc.) in the raw_dict.
		periods = {
			'permanent': self.get_by_path(self.raw_dict, ['essentials', 'originalSalary', 'types', 'permanent', 'period']),
			'b2b': self.get_by_path(self.raw_dict, ['essentials', 'originalSalary', 'types', 'b2b', 'period']),
			'zlecenie': self.get_by_path(self.raw_dict, ['essentials', 'originalSalary', 'types', 'zlecenie', 'period']),
		}

		# None counter to validate if there is at least one populated agreement
		# type.
		Nones_found = 0

		for agr_type, period in periods.items():
			# If period is None then this agreeent type has no salary posted, so
			# we can just skip to the next one.
			if period is None:
				Nones_found += 1
				continue

			# At 3 Nones we failed to find any salary entries (i.e. all
			# agreement types were empty in terms of salary number).
			if Nones_found == 3:
				self.log(3000)
				break

			# Get the salary range which is a list of two integers - min and max
			# salary for given period.
			sal_range =  self.get_by_path(self.raw_dict, ['essentials', 'originalSalary', 'types', agr_type, 'range'])

			# In case there is only one salary number given (min equal to max),
			# convert the range list from one element to two matching elements.
			if len(sal_range) == 1:
				sal_range.append(sal_range[0])

			# Convert all salaries to monthly basis. Assumptions:
			# -there are 168 working hours in a month,
			# -there are 8 working hours in a day.
			if period == 'Hour':
				sal_range = [hourly * 168 for hourly in sal_range]
			elif period == 'Day':
				sal_range = [(daily / 8) * 168 for daily in sal_range]
			elif period == 'Week':
				sal_range = [(weekly / 40) * 168 for weekly in sal_range]
			elif period == 'Month':
				pass
			else:
				self.log(3001)

			# Populate clean_dict.
			if agr_type == 'permanent':
				self.clean_dict['SalaryMinUoP'] = min(sal_range)
				self.clean_dict['SalaryMaxUoP'] = max(sal_range)
			elif agr_type == 'b2b':
				self.clean_dict['SalaryMinB2B'] = min(sal_range)
				self.clean_dict['SalaryMaxB2B'] = max(sal_range)
			elif agr_type == 'zlecenie':
				self.clean_dict['SalaryMinOther'] = min(sal_range)
				self.clean_dict['SalaryMaxOther'] = max(sal_range)

	def populate_skills(self):
		for skill_category in ('musts', 'nices'):
			skills = self.get_by_path(self.raw_dict, ['requirements', skill_category])
			if skills is not None:
				for skill in skills:
					clean_dict_key = skill_category.title()[:-1] + 'Skills'
					self.clean_dict[clean_dict_key].add(skill['value'])

		langs = self.get_by_path(self.raw_dict, ['requirements', 'languages'])
		if langs is not None:
			for lang in langs:
				self.clean_dict_key = lang['type'].title() + 'Skills'
				self.clean_dict[clean_dict_key].add(lang['code'])

	def populate_locations(self):
		location = self.get_by_path(self.raw_dict, ['location'])

		# Edge case: no location at all.
		if location is None:
			return

		# Edge case: insufficient location details.
		if not 'places' in location or len(location['places']) == 0:
			return

		# No edge cases.
		for place in location['places']:
			if place['city'] == 'Remote':
				self.clean_dict['AvailableRemote'] = True
				self.clean_dict['Locations'].add('Remote')
			elif 'country' in place and place['country']['code'] == 'POL':
				self.clean_dict['AvailableInPoland'] = True
				self.clean_dict['Locations'].add('POL')
			elif 'country' in place and place['country']['code'] != 'POL':
				self.clean_dict['Locations'].add(place['country']['code'])
			else:
				self.log(3002)
