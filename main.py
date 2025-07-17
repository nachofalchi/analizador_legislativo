from scraping.scrape import scrape_votation_metadata, scrape_votation_data
from src.directory.utils import get_elems_in_directory

from src.processing.analyzer import determine_loyalty_votation
import pandas as pd

from crud import save_votation_metadata
from database.connections import SessionLocal, Base, engine
from src.database.models import VotationMetadata, DeputiesVoting

from paths import VOTATIONS_DIR

def main():
	Base.metadata.create_all(bind=engine)
	pass

def update_votation_metadata():
	"""
	Updates the laws metadata by scraping the latest votation data.
	"""
	new_law_list = scrape_votation_metadata(year=2024)

	db = SessionLocal()

	new_votation_count = save_votation_metadata(db, new_law_list)

	db.close()

	print(f"Added {new_votation_count} new votations metadata to the database.")

	return new_votation_count

def update_votation_data():
	"""
	Scrapes votation data for each votation in the database.
	"""
	db = SessionLocal()
	votation_metadata = db.query(VotationMetadata).filter(VotationMetadata.loaded == False).all()

	for votation in votation_metadata:
		votation_id = votation.id
		print(f"Scraping data for votation {votation_id}...")
		votation_data = scrape_votation_data(votation_id)
		
		if votation_data:
			print(f"Processing votation data for {votation_id}...")
			print(f"Found {len(votation_data)} votes for votation {votation_id}.")
			for data in votation_data:
				data['vote_id'] = votation_id
				deputy_vote = DeputiesVoting(**data)
				db.add(deputy_vote)
		votation.loaded = True
		db.add(votation)

	db.commit()
	db.close()
	print("Votation data updated successfully.")

def analyze_votations():
	"""
	Returns a DataFrame with the analysis of votations.
	Each row contains the block name, deputy name, average loyalty, total votes,
	and officialism support.
	"""
	db = SessionLocal()

	query = db.query(VotationMetadata.id).all()
	id_list = [int(row.id) for row in query]

	votations_result = []

	for id in id_list:

		query = db.query(DeputiesVoting).filter(DeputiesVoting.vote_id == id)

		votation_df = pd.read_sql(query.statement, db.bind, index_col='id')
		

		votation_result = determine_loyalty_votation(votation_df)

		votations_result.append(votation_result)

	db.close()

	df_merged = pd.concat(votations_result)

	# print(df_merged)

	final_analysis_df = df_merged.groupby(['block','deputy']).agg(
            average_loyalty=('loyalty', 'mean'),
            total_votes=('vote', 'count'),
			officialism_support=('supported_officialism', 'mean'),
			accerted=('accerted', 'count')
        )

	return final_analysis_df

def get_votations_metadata():
	"""
	Returns a DataFrame with the votation metadata.
	Each row contains the votation ID, date, title, type, result, loaded status, and analyzed status.
	"""
	db = SessionLocal()
	query = db.query(VotationMetadata)
	df = pd.read_sql(query.statement, db.bind, index_col='id')
	db.close()
	return df

def get_votation_data(votation_id):
	"""
	Returns a DataFrame with the votation data for the given votation ID.
	Each row contains the vote ID, deputy name, block name, province, and vote.
	"""
	db = SessionLocal()
	query = db.query(DeputiesVoting).filter(DeputiesVoting.vote_id == votation_id)
	df = pd.read_sql(query.statement, db.bind, index_col='id')
	db.close()
	return df

if __name__ == "__main__":
	main()