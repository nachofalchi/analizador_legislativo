import streamlit as st
import pandas as pd
from src.data_loader import load_analysis_data

def show_predictions():
	"""Display predictions page with top 10 deputies by prediction accuracy."""
	# Back to home button
	if st.button("← Volver al inicio"):
		st.session_state.page = 'home'
		st.rerun()
	
	st.title("🎯 Predicciones Legislativas")
	st.header("Top 10 Diputados con Mayor Precisión Predictiva")
	
	st.markdown("""
	Estos son los diputados que más aciertos tienen al predecir el resultado final 
	de las votaciones basándose en su historial de votos.
	""")
	df_analisis = load_analysis_data()
	top_predictors = df_analisis.sort_values(
		by=['total_votes', 'accerted'], 
		ascending=False
	).head(10)
	st.write("---")
	
	# Display top 10 predictors with enhanced layout
	for i, diputado in enumerate(top_predictors.itertuples(), 1):
		with st.container():
			col_rank, col_info, col_stats = st.columns([0.5, 2, 2])
			
			with col_rank:
				st.markdown(f"### #{i}")
			
			with col_info:
				st.subheader(diputado.deputy)
				st.caption(f"Bloque: {diputado.block}")
			
			with col_stats:
				stat_col1, stat_col2, stat_col3 = st.columns(3)
				
				with stat_col1:
					st.metric(
						label="Aciertos", 
						value=f"{diputado.accerted}"
					)
				
				with stat_col2:
					st.metric(
						label="% Precisión", 
						value=f"{diputado.accerted/diputado.total_votes:.1%}"
					)
				
				with stat_col3:
					st.metric(
						label="Lealtad al Bloque", 
						value=f"{diputado.average_loyalty:.1%}"
					)
			
			st.divider()