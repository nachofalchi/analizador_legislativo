import pandas as pd
import numpy as np
from paths import RAW_DATA_DIR, PROCESSED_DATA_DIR, DATA_DIR

def get_blocks_data(res_votation):
    """
    Returns a dataframe of blocks from the votation data.
	Each entry contains the block name, the number of votes, and the counts of each voting preference.
	Vote preference is determined by comparing the number of affirmative and negative votes
    """
    counts_df = res_votation.groupby('BLOQUE')['¿CÓMO VOTÓ?'].value_counts().unstack(fill_value=0)

    vote_types = ['AFIRMATIVO', 'NEGATIVO', 'ABSTENCION', 'SIN VOTAR', 'AUSENTE']
    for v_type in vote_types:
        if v_type not in counts_df.columns:
            counts_df[v_type] = 0

    counts_df['count'] = counts_df.sum(axis=1)
    counts_df['preference'] = (counts_df['AFIRMATIVO'] > counts_df['NEGATIVO']).astype(int)

    counts_df = counts_df.rename(columns={
        'AFIRMATIVO': 'affirmatives',
        'NEGATIVO': 'negatives',
        'ABSTENCION': 'abstentions',
        'SIN VOTAR': 'not_voted',
        'AUSENTE': 'absents'
    })
    
    counts_df.index.rename('block', inplace=True)
    
    counts_df.columns.rename('category', inplace=True)

    return counts_df

def analyze_votation(filename):
	"""
	Analyzes the votation data and returns a DataFrame with the results.
	deputies_df: DataFrame with individual deputy voting behavior and loyalty.
	"""
	if check_if_processed(filename):
		print(f'File {filename} has already been processed.')
		return None, None
	
	print(f'Processing votation data for {filename}...')

	votation_df = pd.read_csv(RAW_DATA_DIR /filename)


	blocks_df = get_blocks_data(votation_df)
	deputies_df = analyze_deputies(votation_df, blocks_df, filename)
	deputies_df.to_csv(PROCESSED_DATA_DIR / f'deputies.csv')
	print(f'Processed votation data')

def analyze_deputies(votation_df, blocks_df,vote_id):
	"""
	Analyzes votation data by merging block preferences with individual votes
	and returns a DataFrame with all columns 
	"""
	block_preferences = blocks_df[['preference']]

	merged_df = pd.merge(
		votation_df,
		block_preferences,
		left_on='BLOQUE',
		right_index=True,
		how='left'
	)

	cond_loyal_afirmative = (merged_df['preference'] == 1) & (merged_df['¿CÓMO VOTÓ?'] == 'AFIRMATIVO')
	cond_loyal_negative = (merged_df['preference'] == 0) & (merged_df['¿CÓMO VOTÓ?'] == 'NEGATIVO')

	merged_df['loyalty'] = np.where(cond_loyal_afirmative | cond_loyal_negative, 1, 0)

	rename_map = {
		'BLOQUE': 'block',
		'DIPUTADO': 'deputy',
		'¿CÓMO VOTÓ?': 'vote'
	}

	merged_df.rename(columns=rename_map, inplace=True)
      
	merged_df['vote_id'] = vote_id

	deputies_df = merged_df[['block', 'deputy', 'vote', 'loyalty']]
	deputies_df.set_index(['block', 'deputy'], inplace=True)


	return deputies_df

def check_if_processed(filename):
	"""
	Checks if the votation data has already been processed.
	Returns True if processed, False otherwise.
	"""
	file_status_df = pd.read_csv(DATA_DIR / 'already_processed.csv')
	status = file_status_df.loc[file_status_df['file_name'] == filename, 'processed']
	
	if status.empty:
		return False
	else:
		return status.iloc[0] == 1