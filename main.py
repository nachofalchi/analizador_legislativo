from src.processing.analyzer import analyze_votation
from scraping.scrape import scrape_laws_metadata
from src.directory.utils import get_elems_in_directory

from paths import VOTATIONS_DIR

def main():
	scrape_laws_metadata()

	votation_elems = get_elems_in_directory(VOTATIONS_DIR)
	for votation_name in votation_elems:
		votation_id = int(votation_name[:4])
		analyze_votation(votation_id)

if __name__ == "__main__":
	main()