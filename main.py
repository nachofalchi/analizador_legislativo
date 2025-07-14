from src.processing.analyzer import analyze_votation, check_if_processed
from src.directory.utils import get_elems_in_directory

from paths import RAW_DATA_DIR

def main():
	raw_data_elems = get_elems_in_directory(RAW_DATA_DIR)
	filename = raw_data_elems[0] if raw_data_elems else None
	
	results = analyze_votation(filename)
	print(results)

if __name__ == "__main__":
	main()