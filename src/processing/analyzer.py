import pandas as pd
import numpy as np
from pathlib import Path

def get_blocks_data(votation_df):
    """
    Returns a dataframe of blocks from the votation data.
	Each entry contains the block name, the number of votes, and the counts of each voting preference.
	Vote preference is determined by comparing the number of affirmative and negative votes
    """
    counts_df = votation_df.groupby('block')['vote'].value_counts().unstack(fill_value=0)

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

def analyze_votation(id):
	"""
	Analyzes the votation data and returns a DataFrame with the results.
	deputies_df: DataFrame with individual deputy voting behavior and loyalty.
	"""
	if check_if_analyzed(id):
		print(f'File {id} has already been processed.')
		return None
	
	print(f'Processing votation data for {id}...')

	votation_df = pd.read_csv(f'data/votations/{id}.csv')


	blocks_df = get_blocks_data(votation_df)

	deputies_df = analyze_deputies(votation_df, blocks_df, id)    

	old_deputies_data_df = load_deputies_data()
      
	updated_deputies_df = pd.concat([old_deputies_data_df, deputies_df])

	updated_deputies_df.to_csv('data/processed/deputies.csv')

	mark_as_analyzed(id)

def analyze_deputies(votation_df, blocks_df,votation_id):
	"""
	Analyzes votation data by merging block preferences with individual votes
	and returns a DataFrame with all columns 
	"""
	block_preferences = blocks_df[['preference']]

	merged_df = pd.merge(
		votation_df,
		block_preferences,
		left_on='block',
		right_index=True,
		how='left'
	)


	cond_loyal_afirmative = (merged_df['preference'] == 1) & (merged_df['vote'] == 'AFIRMATIVO')
	cond_loyal_negative = (merged_df['preference'] == 0) & (merged_df['vote'] == 'NEGATIVO')

	merged_df['loyalty'] = np.where(cond_loyal_afirmative | cond_loyal_negative, 1, 0)
      
	merged_df['vote_id'] = votation_id

	deputies_df = merged_df[['block', 'name', 'vote', 'loyalty']]
	deputies_df.set_index(['block', 'name'], inplace=True)


	return deputies_df

def check_if_analyzed(id):
	"""
	Checks if the votation data has already been analyzed.
	Returns True if processed, False otherwise.
	"""
	law_metadata_df = pd.read_csv('data/law_metadata.csv')
	status = law_metadata_df.loc[law_metadata_df['id'] == id, 'analyzed']
	
	if status.empty:
		return False
	else:
		return status.iloc[0] == 1
	
def mark_as_analyzed(id):
	"""
	Marks the votation data as analyzed in the law metadata.
	"""
	law_metadata_df = pd.read_csv('data/law_metadata.csv')
	law_metadata_df.loc[law_metadata_df['id'] == id, 'analyzed'] = 1
	law_metadata_df.to_csv('data/law_metadata.csv', index=False)
	print(f'Marked votation {id} as analyzed.')

def load_deputies_data():
    """
    Load existing deputies data from CSV file.
    Returns empty DataFrame if file doesn't exist.
    """
    file_path = Path('data/processed/deputies.csv')
    
    try:
        if not file_path.exists():
            print("File couldnt be found. New will be created.")
            return pd.DataFrame()
            
        df = pd.read_csv(file_path, index_col=['block', 'name'])
        print(f"File found with {len(df)} registers.")
        return df
        
    except pd.errors.EmptyDataError:
        print("File exists but its empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading the file: {e}")
        return pd.DataFrame()