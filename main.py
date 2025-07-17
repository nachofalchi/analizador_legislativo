"""
Legislative Votation Analysis Module

This module provides functionality to scrape, process, and analyze 
Argentine legislative voting data, including deputy loyalty and 
support for government positions.
"""

from src.scraping.scrape import scrape_votation_metadata, scrape_votation_data
from src.processing.analyzer import determine_loyalty_votation
import pandas as pd

from database.crud import save_votation_metadata
from database.connections import SessionLocal, Base, engine
from src.database.models import VotationMetadata, DeputiesVoting

from paths import VOTATIONS_DIR


def main():
	"""Main entry point for the legislative analysis application."""
	Base.metadata.create_all(bind=engine)
	analyze_votations()


def update_votation_metadata():
	"""
	Update the laws metadata by scraping the latest votation data.
	
	Returns:
		int: Number of new votations added to the database
	"""
	new_law_list = scrape_votation_metadata(year=2024)

	db = SessionLocal()

	new_votation_count = save_votation_metadata(db, new_law_list)

	db.close()

	print(f"Added {new_votation_count} new votations metadata to the database.")

	return new_votation_count


def update_votation_data():
	"""
	Scrape votation data for each votation in the database that hasn't been loaded yet.
	Updates the loaded status for each processed votation.
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
	Analyze all votations and return comprehensive statistics.
	
	Returns:
		pd.DataFrame: Grouped analysis with deputy loyalty statistics,
					 indexed by block and deputy name, with columns:
					 - average_loyalty: Mean loyalty to party block
					 - total_votes: Number of votes cast by deputy
					 - officialism_support: Support rate for government positions
					 - accerted: Number of correct predictions (placeholder)
	"""
	db = SessionLocal()

	# Get all votation IDs from database
	query = db.query(VotationMetadata.id).all()
	id_list = [int(row.id) for row in query]

	votations_result = []

	for votation_id in id_list:
		# Query votation data for current ID
		query = db.query(DeputiesVoting).filter(DeputiesVoting.vote_id == votation_id)
		votation_df = pd.read_sql(query.statement, db.bind, index_col='id')
		
		# Exclude the president from analysis (not a regular deputy)
		votation_df = votation_df[votation_df['vote'] != 'PRESIDENTE']

		# Analyze loyalty for this specific votation
		votation_result = determine_loyalty_votation(votation_df)
		votations_result.append(votation_result)

	db.close()

	# Combine all votation results
	df_merged = pd.concat(votations_result)

	# Create a new column for counting only AFIRMATIVO and NEGATIVO votes
	df_merged['vote_count'] = df_merged['vote'].apply(lambda x: 1 if x in ['AFIRMATIVO', 'NEGATIVO'] else 0)

	# Group by block and deputy to get aggregate statistics
	final_analysis_df = df_merged.groupby(['block', 'deputy']).agg(
		average_loyalty=('loyalty', 'mean'),
		total_votes=('vote_count', 'sum'),
		total_participation=('vote', 'count'),
		officialism_support=('supported_officialism', 'mean'),
		accerted=('accerted', 'sum'),
		absent=('absent', 'sum'),
		not_voted=('not_voted', 'sum'),
		abstention=('abstention', 'sum')
	)
	
	return final_analysis_df

def get_votations_metadata():
	"""
	Retrieve all votation metadata from the database.
	
	Returns:
		pd.DataFrame: Votation metadata with columns including ID, date, title, 
					 type, result, loaded status, and analyzed status
	"""
	db = SessionLocal()
	query = db.query(VotationMetadata)
	df = pd.read_sql(query.statement, db.bind, index_col='id')
	db.close()
	return df


def get_votation_data(votation_id):
	"""
	Retrieve votation data for a specific votation ID.
	
	Args:
		votation_id (int): The ID of the votation to retrieve
		
	Returns:
		pd.DataFrame: Votation data with columns including vote ID, deputy name,
					 block name, province, and vote
	"""
	db = SessionLocal()
	query = db.query(DeputiesVoting).filter(DeputiesVoting.vote_id == votation_id)
	df = pd.read_sql(query.statement, db.bind, index_col='id')
	db.close()
	return df


if __name__ == "__main__":
	main()