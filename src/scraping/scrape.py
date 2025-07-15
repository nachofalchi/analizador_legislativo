import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_law_data(type = 'ley', year = 2024):
	"""
	Scrape metadata and the vote from each deputy from the law voting website.
	Parameters:
		type (str): Type of voting to search for (default is 'ley').
		year (int): Year of the voting to search for (default is 2025
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
		print("Request was successful!")

		new_law_metadata_df = parse_law_list(response.text)

		old_law_metadata_df = pd.read_csv('data/law_metadata.csv', index_col='id')
		if old_law_metadata_df.empty:
			print("No previous law metadata found, creating new file.")
		else:
			print("Previous law metadata found, updating with new data.")

		updated_df = pd.concat([old_law_metadata_df, new_law_metadata_df]).drop_duplicates(keep='last')

		updated_df.to_csv('data/law_metadata.csv')
		print("Law metadata saved to CSV.")
	else:
		print(f"Request failed with status code: {response.status_code}")

def parse_law_list(html_content):
	"""
	Parses the HTML content (should be the main Camara de
	Diputados website) to extract law voting data.
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
			'processed': 0
		})
	return pd.DataFrame(laws_data).set_index('id')


scrape_law_data()