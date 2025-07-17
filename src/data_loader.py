import streamlit as st
import pandas as pd
from main import analyze_votations

@st.cache_data
def load_analysis_data():
	"""
	Execute complete analysis and return a flattened DataFrame.
	
	Returns:
		pd.DataFrame: Analysis results with deputy information
	"""
	print("Executing complete analysis...")
	
	df_votation = analyze_votations()
	df = df_votation.reset_index()
	
	return df