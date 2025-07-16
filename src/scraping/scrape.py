import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime

def scrape_votation_metadata(type = 'ley', year = 2025):
	"""
	Scrape metadata and the vote from each deputy from the law voting website.
	Parameters:
		type (str): Type of voting to search for (default is 'ley').
		year (int): Year of the voting to search for (default is 2025)
	Returns:
		List of dictionaries with id, date, title, type, result, downloaded and analyzed.
	"""
	url = 'https://votaciones.hcdn.gob.ar/votaciones/search'
	payload = {
		'txtSearch': type,
		'anoSearch': f'{year}'
	}
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

	response = communicate_with_website(url, payload, headers)

	new_law_metadata = parse_votation_list(response.text)

	return new_law_metadata


def communicate_with_website(url, payload, headers):
	"""
	Communicates with the website to get the HTML content.
	Parameters:
		url (str): The URL to send the request to.
		payload (dict): The data to send in the POST request.
		headers (dict): The headers to include in the request.
	Returns:
		response: The response object from the request.
	"""
	try:
		response = requests.post(url, data=payload, headers=headers)
		response.raise_for_status()
		return response
	except requests.RequestException as e:
		print(f"An error occurred: {e}")
		return None

def parse_votation_list(html_content):
	"""
	Parses the HTML content (should be the main Camara de
	Diputados website) to extract laws meta data. Returns
	a List of dictionaries with id, date, title, type, result,
	downloaded and analyzed.
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
			'date': datetime.strptime(cells[0].text.strip()[:10], '%d/%m/%Y').date(), 
			'title': cells[1].text.strip(),
			'type': cells[2].text.strip(),
			'result': 'positive' if cells[2].text.strip() == 'AFIRMATIVO' else 'negative',
			'loaded': 0,
			'analyzed': 0
		})
	return laws_data


def scrape_votation_data(id : int):
	"""
	Scrapes the votation data for the given ID
	"""

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
			'vote_id': id,
			'deputy' : cells[1].text.strip(),
			'block' : cells[2].text.strip(),
			'province' : cells[3].text.strip(),
			'vote' : cells[4].text.strip(),
		})

	return votation_data