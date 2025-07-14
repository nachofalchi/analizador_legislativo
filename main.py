from src.processing.analyzer import analyze_votation

def main():
	filename = "142-22-10"
	results = analyze_votation(filename)
	print(results)

if __name__ == "__main__":
	main()