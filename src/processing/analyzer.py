import pandas as pd
from paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

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
	"""
    res_votation = pd.read_csv(RAW_DATA_DIR /f'{filename}.csv')
    res_votation.to_csv(PROCESSED_DATA_DIR/f'{filename}_processed.csv')
    processed_votation = get_blocks_data(res_votation)
    print('Processed votation data:')
    return processed_votation




