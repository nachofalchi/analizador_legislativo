import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

def scrape_laws_metadata(type = 'ley', year = 2025):
	"""
	Scrape metadata and the vote from each deputy from the law voting website.
	Parameters:
		type (str): Type of voting to search for (default is 'ley').
		year (int): Year of the voting to search for (default is 2025)
	Returns:
		None
	"""
	url = 'https://votaciones.hcdn.gob.ar/votaciones/search'

	payload = {
		'txtSearch': type,
		'anoSearch': f'{year}'
	}

	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

	response = requests.post(url, data=payload, headers=headers)

	if response.status_code == 200:

		new_law_metadata_df = parse_law_list(response.text)

		old_law_metadata_df = load_law_metadata()

		existing_ids = old_law_metadata_df.index.astype(str)
		new_ids = new_law_metadata_df.index.astype(str)
	
		truly_new_laws = new_law_metadata_df[~new_ids.isin(existing_ids)]

		print(f"Found {len(truly_new_laws)} new laws to add.")

		if not truly_new_laws.empty:
			updated_df = pd.concat([old_law_metadata_df, truly_new_laws])
			updated_df.to_csv('data/law_metadata.csv')
			print("Law metadata updated with new laws.")
			scrape_law_data(updated_df)

	else:
		print(f"Request failed with status code: {response.status_code}")


def load_law_metadata():
    """
    Load existing law metadata from CSV file.
    Returns empty DataFrame if file doesn't exist.
    """
    file_path = Path('data/law_metadata.csv')
    
    try:
        if not file_path.exists():
            print("File couldnt be found. New will be created.")
            return pd.DataFrame()
            
        df = pd.read_csv(file_path, index_col='id')
        print(f"File found with {len(df)} registers.")
        return df
        
    except pd.errors.EmptyDataError:
        print("File exists but its empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading the file: {e}")
        return pd.DataFrame()

	

def parse_law_list(html_content):
	"""
	Parses the HTML content (should be the main Camara de
	Diputados website) to extract laws meta data. Returns
	a DataFrame with the laws metadata.
	"""

	laws_data = []

	soup = BeautifulSoup(html_content, 'html.parser')

	table = soup.find('tbody', attrs={'id': "container-actas"})

	table_rows = table.find_all('tr')
	for row in table_rows:
		id = row.get('id')
		cells = row.find_all('td')
		laws_data.append( {
			'id': id,
			'date': cells[0].text.strip()[:10],
			'title': cells[1].text.strip(),
			'type': cells[2].text.strip(),
			'result': 'positive' if cells[2].text.strip() == 'AFIRMATIVO' else 'negative',
			'processed': 0,
			'analyzed': 0
		})
	return pd.DataFrame(laws_data).set_index('id')


def scrape_law_data(law_df):
	"""
	Scrapes the votation data for each law in the provided DataFrame.
	"""

	unprocessed_laws = law_df[law_df['processed'] == 0]
	ids = unprocessed_laws.index.tolist()

	print(f"Found {len(ids)} laws to scrape votation data for.")

	for id in ids:

		print(f"Scraping votation data for law ID: {id}")
		votation_data = []

		url = f'https://votaciones.hcdn.gob.ar/votacion/{id}'
		
		try:
			response = requests.get(url)
			
		except Exception as e:
			print(f"Ocurrió un error: {e}")

		soup = BeautifulSoup(response.text, 'html.parser')
			
		table = soup.find('table', attrs={'id': "myTable"})

		table_body = table.find('tbody')

		table_rows = table_body.find_all('tr')

		for row in table_rows:
			cells = row.find_all('td')
			votation_data.append({
				'name' : cells[1].text.strip(),
				'block' : cells[2].text.strip(),
				'province' : cells[3].text.strip(),
				'vote' : cells[4].text.strip(),
			})
		
		votation_df = pd.DataFrame(votation_data)

		votation_df.to_csv(f'data/votations/{id}.csv', index=False)

		law_df.loc[id, 'processed'] = 1
            
		law_df.to_csv('data/law_metadata.csv')

	return votation_df

	

scrape_laws_metadata(type='ley', year=2025)