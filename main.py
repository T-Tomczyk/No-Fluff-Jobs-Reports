import scripts.data_stage_manager as sm

stage_manager = sm.DataStageManager()
# stage_manager.add_to_found('7g49hgdh')
# stage_manager.export_stages()
print(stage_manager.stages)


# Get a list of all offer IDs visible on No Fluff Jobs at the moment, together
# with the page index they were found at (for analyzing if we should always
# scrape all the pages or if maybe only some is enough).
pass

# For each offer_id see what stage it is in.
pass

# Each offer_id that's not in any of the stages goes to 'found'.
# Export the pickle.
pass

# Try and download .json files for all of the offers in 'found' using the API.
# Each successful download causes the offer to go from 'found' to 'downloaded'.
pass

# For each offer in 'downloaded' extract the key info from and then try and
# export it to the database. If success, move from 'downloaded' to 'exported'.
pass
