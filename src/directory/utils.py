
def get_elems_in_directory(directory):
	"""
	Returns a list of all files in the given directory.
	"""
	return [f.name for f in directory.iterdir() if f.is_file()]