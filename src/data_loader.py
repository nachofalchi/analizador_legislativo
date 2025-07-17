import streamlit as st
import pandas as pd
import sys
import os

# Añadir directorio raíz al path para importar main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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