import pandas as pd
import numpy as np

def get_blocks_data(votation_df):
    """
    Returns a dataframe with the information of the blocks from the votation data.
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

def determine_loyalty_votation(votation_df):
	"""
	Analyzes the votation data and returns a DataFrame with the results.
	deputies_df: DataFrame with individual deputy voting behavior and loyalty.
	"""

	blocks_df = get_blocks_data(votation_df)

	deputies_df = compare_block_deputies_preference(votation_df, blocks_df)    
	
	return deputies_df

def compare_block_deputies_preference(votation_df, blocks_df):
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

	# Loyalty calculation
	cond_loyal_afirmative = (merged_df['preference'] == 1) & (merged_df['vote'].isin(['AFIRMATIVO']))
	cond_loyal_negative = (merged_df['preference'] == 0) & (merged_df['vote'].isin(['NEGATIVO']))
	merged_df['loyalty'] = np.where(cond_loyal_afirmative | cond_loyal_negative, 1, 0)
    
      
	# Prediction accuracy
	votation_result = 1 if len(votation_df.loc[votation_df['vote'] == 'AFIRMATIVO']) > len(votation_df) else 0
	accerted_afirmative = (votation_result == 1) & (merged_df['vote'].isin(['AFIRMATIVO']))
	accerted_negative = (votation_result == 0) & (merged_df['vote'].isin(['NEGATIVO']))  
	merged_df['accerted'] = np.where(accerted_afirmative | accerted_negative, 1, 0)
    
	# Officialism support calculation
	officialism_preference = blocks_df.loc['La Libertad Avanza', 'preference']
	cond_loyal_officialism_affirmative = (officialism_preference == 1) & (merged_df['vote'].isin(['AFIRMATIVO', 'PRESIDENTE']))
	cond_loyal_officialism_negative = (officialism_preference == 0) & (merged_df['vote'].isin(['NEGATIVO', 'AUSENTE', 'SIN VOTAR', 'ABSTENCION']))
	merged_df['supported_officialism'] = np.where(cond_loyal_officialism_affirmative | cond_loyal_officialism_negative, 1, 0) 
      
	

	deputies_df = merged_df[['block', 'deputy', 'vote', 'loyalty', 'supported_officialism','accerted']]
	deputies_df.set_index(['block', 'deputy'], inplace=True)

	return deputies_df
	