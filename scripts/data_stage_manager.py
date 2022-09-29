import pickle

class DataStageManager:
	'''
	This class helps keep track of where various offers are at any given time.

	There are three stages of the data pipeline:
	1) found means an offer was found to exist and nothing else was done
	about it,
	2) downloaded means the .json file was downloaded onto the local directory
	from the API service,
	3) exported means the key info was exracted from the .json file and fed to
	the database.

	Each stage has its corresponding set. Sets are populated with external
	Offer IDs as strings.

	The data can be pickled or unpickled (saved to or loaded from permanent
	storage) at any time.
	'''

	def __init__(self):
		with open(f'local/data_stages/stages.pickle', 'rb') as f:
			self.stages = pickle.load(f)

	def export_stages(self):
		with open('local/data_stages/stages.pickle', 'wb') as f:
			pickle.dump(self.stages, f, pickle.HIGHEST_PROTOCOL)

	def add_to_found(self, offer_id):
		self.stages['found'].add(offer_id)

	def move_from_found_to_downloaded(self, offer_id):
		self.stages['downloaded'].add(offer_id)
		self.stages['found'].discard(offer_id)

	def move_from_downloaded_to_exported(self, offer_id):
		self.stages['exported'].add(offer_id)
		self.stages['downloaded'].discard(offer_id)
