import streamlit as st
import pandas as pd
from src.data_loader import load_analysis_data
from main import get_votations_metadata, get_votation_data
from datetime import datetime
import pandas as pd
import plotly.express as px

def show_home():
	"""Display home page with navigation buttons and main dashboard."""
	# Load data
	df_votations = load_analysis_data()
	df_votations_metadata = get_votations_metadata()

	# Page header
	st.title("Analizador Legislativo Argentino")
	st.write(f"Datos actualizados al {datetime.now().strftime('%d/%m/%Y')}")
	st.divider()
	 
	# Calculate key metrics for dashboard
	votations_count = len(df_votations_metadata.index.unique())
	cohesion_general = df_votations['average_loyalty'].mean()
	bloque_mas_cohesivo = df_votations.groupby('block')['average_loyalty'].mean().idxmax()
	ultima_votacion = pd.to_datetime(df_votations_metadata['date']).max().strftime('%d/%m/%Y')

	# Display key metrics in columns
	col1, col2, col3, col4 = st.columns(4)
	
	with col1:
		st.metric(label="Votaciones Analizadas", value=votations_count)
	
	with col2:
		st.metric(label="Cohesión Promedio General", value=f"{cohesion_general:.1%}")
	
	with col3:
		st.metric(label="Bloque más Cohesivo", value=bloque_mas_cohesivo)
	
	with col4:
		st.metric(label="Última Votación Registrada", value=ultima_votacion)

	st.divider()
	
	# Chamber composition pie chart section
	st.header("Composición de la Cámara")

	# Get latest votation data for chamber composition
	df = get_votations_metadata()
	latest_votation_metadata_df_entry = df.loc[df['date'] == df['date'].max()]
	latest_votation_id = latest_votation_metadata_df_entry.index[0]

	latest_votation_df = get_votation_data(latest_votation_id)
	deputies_count = len(latest_votation_df['deputy'].unique())

	# Prepare data for pie chart visualization
	votation_df = latest_votation_df['block'].value_counts().reset_index()
	votation_df.columns = ['Bloque', 'Cantidad']
	votation_df['Porcentaje'] = (votation_df['Cantidad'] / deputies_count * 100).round(1)

	# Create interactive pie chart
	fig = px.pie(
		votation_df, 
		values='Cantidad',
		names='Bloque',
		title=f'Distribución de Diputados por Bloque (Total: {deputies_count})',
		hover_data=['Porcentaje'],
		custom_data=['Porcentaje']
	)

	# Customize hover information for better user experience
	fig.update_traces(
		hovertemplate="<b>%{label}</b><br>" +
					 "Diputados: %{value}<br>" +
					 "Porcentaje: %{customdata[0]:.1f}%<extra></extra>"
	)

	# Customize layout for better presentation
	fig.update_layout(
		title={
			'text': f"Distribución de Diputados por Bloque<br><sup>Total: {deputies_count} Diputados</sup>",
			'y': 0.95,
			'x': 0.5,
			'xanchor': 'center',
			'yanchor': 'top',
			'font': {'size': 20}
		},
		width=800,
		height=600
	)

	st.plotly_chart(fig, use_container_width=True)
	st.divider()
	
	# Loyalty ranking section
	st.header("Ranking de Lealtad Partidaria")
	
	# Filter deputies with significant participation (at least half of total votes)
	total_votaciones = len(df_votations_metadata.index.unique())
	umbral_minimo_votos = total_votaciones // 2
	
	df_analisis_filtrado = df_votations[df_votations['total_votes'] >= umbral_minimo_votos]
	
	# Calculate top and bottom loyalty rankings
	top_5_leales = df_analisis_filtrado.sort_values(
		by=['average_loyalty', 'total_votes'], 
		ascending=False
	).head(5)
	
	flop_5_leales = df_analisis_filtrado.sort_values(
		by=['average_loyalty', 'total_votes'], 
		ascending=True
	).head(5)
	
	st.caption(
		f"Ranking basado en diputados con al menos {umbral_minimo_votos} "
		f"votaciones de {total_votaciones} totales ({len(df_analisis_filtrado)} diputados califican)"
	)
	
	# Display rankings in two columns
	col_top, col_flop = st.columns(2)
	
	with col_top:
		st.subheader("5 Más Leales")
		st.caption("Diputados con mayor lealtad a su bloque")
		
		for i, diputado in enumerate(top_5_leales.itertuples(), 1):
			with st.container():
				st.markdown(f"""
				**#{i} {diputado.deputy}**  
				*{diputado.block}*  
				Lealtad: **{diputado.average_loyalty:.1%}** | Votos: {diputado.total_votes}
				""")
				
				# Visual progress bar for loyalty (green)
				progress_html = f"""
				<div style="background-color: #e9ecef; border-radius: 10px; height: 8px; width: 100%; margin: 5px 0;">
					<div style="background-color: #28a745; width: {diputado.average_loyalty*100}%; border-radius: 10px; height: 100%;"></div>
				</div>
				"""
				st.markdown(progress_html, unsafe_allow_html=True)
				
				if i < 5:
					st.markdown("---")
	
	with col_flop:
		st.subheader("5 Menos Leales")
		st.caption("Diputados con menor lealtad a su bloque")
		
		for i, diputado in enumerate(flop_5_leales.itertuples(), 1):
			with st.container():
				st.markdown(f"""
				**#{i} {diputado.deputy}**  
				*{diputado.block}*  
				Lealtad: **{diputado.average_loyalty:.1%}** | Votos: {diputado.total_votes}
				""")
				
				# Visual progress bar for loyalty (red for less loyal)
				progress_html = f"""
				<div style="background-color: #e9ecef; border-radius: 10px; height: 8px; width: 100%; margin: 5px 0;">
					<div style="background-color: #dc3545; width: {diputado.average_loyalty*100}%; border-radius: 10px; height: 100%;"></div>
				</div>
				"""
				st.markdown(progress_html, unsafe_allow_html=True)
				
				if i < 5:
					st.markdown("---")

	st.divider()
	
	# Absence ranking section
	st.header("Ranking de Ausencias")
	
	# Calculate absences for deputies with significant participation
	
	top_10_ausentes = df_analisis_filtrado.nlargest(10, 'absent')
	
	st.caption(f"Ranking de ausencias basado en diputados con al menos {umbral_minimo_votos} votaciones")
	st.subheader("Diputados con Más Ausencias")
	
	# Display absence ranking with styled containers
	for i, diputado in enumerate(top_10_ausentes.itertuples(), 1):
		background_color = "#f8f9fa" if i % 2 == 0 else "#ffffff"
		
		container_html = f"""
		<div style="background-color: {background_color}; padding: 15px; border-radius: 8px; margin: 5px 0; border-left: 4px solid #dc3545;">
			<div style="display: flex; justify-content: space-between; align-items: center;">
				<div>
					<strong>#{i} {diputado.deputy}</strong><br>
					<em style="color: #6c757d;">{diputado.block}</em>
				</div>
				<div style="text-align: right;">
					<div style="font-size: 18px; font-weight: bold; color: #dc3545;">
						{diputado.absent} ausencias
					</div>
					<div style="color: #6c757d;">
						{diputado.absent/diputado.total_participation*100:.1f}% del total
					</div>
					<div style="color: #6c757d; font-size: 12px;">
						Participó en {diputado.total_participation-diputado.absent}/{diputado.total_participation} votaciones
					</div>
				</div>
			</div>
		</div>
		"""
		st.markdown(container_html, unsafe_allow_html=True)
	
	# General absence statistics
	col1, col2, col3 = st.columns(3)
	
	with col1:
		promedio_ausencias = df_analisis_filtrado['absent'].mean()
		st.metric(
			label="Promedio de Ausencias", 
			value=f"{promedio_ausencias:.1f}"
		)
	
	with col3:
		deputy = top_10_ausentes.iloc[0]
		st.metric(
			label="Máximo de Ausencias", 
			value=f"{deputy.absent} ({deputy.absent/deputy.total_participation*100:.1f}%)"
		)
	
	st.divider()