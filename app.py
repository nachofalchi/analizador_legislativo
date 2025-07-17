import streamlit as st
import pandas as pd
import plotly.express as px
from main import analyze_votations, get_votations_metadata, get_votation_data
from datetime import datetime

st.set_page_config(layout="wide", page_title="Análisis Legislativo")

if 'page' not in st.session_state:
    st.session_state.page = 'home'


@st.cache_data
def load_analysis_data():
    """
    Ejecuta el análisis y devuelve un DataFrame "plano" listo para usar.
    """
    print("Ejecutando análisis completo...")
    
    df_votation = analyze_votations()
    
    df = df_votation.reset_index()
    
    return df

@st.cache_data
def calculate_prediction_accuracy():
    """
    Calcula los aciertos de cada diputado comparando su voto con el resultado final.
    Retorna un DataFrame con los 10 diputados con más aciertos.
    """
    df_analisis = load_analysis_data()
    
    # Aquí necesitarías implementar la lógica para calcular aciertos
    # Por ahora simulo algunos datos de ejemplo
    # En tu implementación real, compararías el voto individual con el resultado final
    
    # Simulación de datos de aciertos (reemplazar con lógica real)
    
    # Ordenar por aciertos y tomar los top 10
    top_predictors = df_analisis.sort_values(by=['total_votes', 'accerted'], ascending=False).head(10)
    
    return top_predictors


def show_home():
	"""Muestra la página de inicio con botones de navegación"""
	df_votations = load_analysis_data()
	df_votations_metadata = get_votations_metadata()

	st.title("Analizador Legislativo Argentino")
    
	st.write(f"Datos actualizados al {datetime.now().strftime('%d/%m/%Y')}")
	st.divider()
     
	# metric 1: count of votations analyzed
	votations_count = len(df_votations_metadata.index.unique())

	# metric 2: average cohesion of the entire chamber
	cohesion_general = df_votations['average_loyalty'].mean()

	# metric 3: most cohesive block
	bloque_mas_cohesivo = df_votations.groupby('block')['average_loyalty'].mean().idxmax()

	# metric 4: date of the last votation
	ultima_votacion = pd.to_datetime(df_votations_metadata['date']).max().strftime('%d/%m/%Y')


	# columns
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
    
	# 
	# Cake graphic
    #  
	st.header("Composición de la Cámara")	

	df = get_votations_metadata()
	latest_votation_metadata_df_entry = df.loc[df['date']==df['date'].max()]
	latest_votation_id = latest_votation_metadata_df_entry.index[0]

	latest_votation_df = get_votation_data(latest_votation_id)
	deputies_count = len(latest_votation_df['deputy'].unique())

	# Crear el DataFrame para el gráfico
	votation_df = latest_votation_df['block'].value_counts().reset_index()
	votation_df.columns = ['Bloque', 'Cantidad']

	# Calcular porcentajes
	votation_df['Porcentaje'] = (votation_df['Cantidad'] / deputies_count * 100).round(1)

	# Crear el gráfico de torta
	fig = px.pie(votation_df, 
				values='Cantidad',
				names='Bloque',
				title=f'Distribución de Diputados por Bloque (Total: {deputies_count})',
				hover_data=['Porcentaje'],
				custom_data=['Porcentaje'])

	# Personalizar el formato del hover
	fig.update_traces(
		hovertemplate="<b>%{label}</b><br>" +
					"Diputados: %{value}<br>" +
					"Porcentaje: %{customdata[0]:.1f}%<extra></extra>"
	)

	# Ajustar el layout
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

	# Mostrar el gráfico
	st.plotly_chart(fig, use_container_width=True)
	
	st.divider()
	
	# Sección TOP 5 y FLOP 5 diputados por lealtad
	st.header("⭐ Ranking de Lealtad Partidaria")
	
	# Obtener todos los datos de análisis
	df_analisis = load_analysis_data()
	
	# Calcular el umbral mínimo de participación (mitad de las votaciones)
	total_votaciones = len(df_votations_metadata.index.unique())
	umbral_minimo_votos = total_votaciones // 2
	
	# Filtrar solo diputados con participación significativa
	df_analisis_filtrado = df_analisis[df_analisis['total_votes'] >= umbral_minimo_votos]
	
	# Calcular TOP 5 y FLOP 5 solo de diputados con participación significativa
	top_5_leales = df_analisis_filtrado.sort_values(by=['total_votes','average_loyalty'], ascending=False).head(5)
	flop_5_leales = df_analisis_filtrado.sort_values(by=['total_votes','average_loyalty'], ascending=True).head(5)
	
	# Mostrar información del filtro aplicado
	st.caption(f"📊 Ranking basado en diputados con al menos {umbral_minimo_votos} votaciones de {total_votaciones} totales ({len(df_analisis_filtrado)} diputados califican)")
	
	# Crear dos columnas para mostrar TOP y FLOP
	col_top, col_flop = st.columns(2)
	
	with col_top:
		st.subheader("🏆 TOP 5 - Más Leales")
		st.caption("Diputados con mayor lealtad a su bloque")
		
		for i, diputado in enumerate(top_5_leales.itertuples(), 1):
			with st.container():
				st.markdown(f"""
				**#{i} {diputado.deputy}**  
				*{diputado.block}*  
				Lealtad: **{diputado.average_loyalty:.1%}** | Votos: {diputado.total_votes}
				""")
				
				# Barra de progreso visual para la lealtad
				progress_html = f"""
				<div style="background-color: #e9ecef; border-radius: 10px; height: 8px; width: 100%; margin: 5px 0;">
					<div style="background-color: #28a745; width: {diputado.average_loyalty*100}%; border-radius: 10px; height: 100%;"></div>
				</div>
				"""
				st.markdown(progress_html, unsafe_allow_html=True)
				
				if i < 5:  # No agregar divider después del último elemento
					st.markdown("---")
	
	with col_flop:
		st.subheader("📉 FLOP 5 - Menos Leales")
		st.caption("Diputados con menor lealtad a su bloque")
		
		for i, diputado in enumerate(flop_5_leales.itertuples(), 1):
			with st.container():
				st.markdown(f"""
				**#{i} {diputado.deputy}**  
				*{diputado.block}*  
				Lealtad: **{diputado.average_loyalty:.1%}** | Votos: {diputado.total_votes}
				""")
				
				# Barra de progreso visual para la lealtad (color rojo para los menos leales)
				progress_html = f"""
				<div style="background-color: #e9ecef; border-radius: 10px; height: 8px; width: 100%; margin: 5px 0;">
					<div style="background-color: #dc3545; width: {diputado.average_loyalty*100}%; border-radius: 10px; height: 100%;"></div>
				</div>
				"""
				st.markdown(progress_html, unsafe_allow_html=True)
				
				if i < 5:  # No agregar divider después del último elemento
					st.markdown("---")
	
	st.divider()
	
	# Sección de Ranking de Ausencias
	st.header("🚫 Ranking de Ausencias")
	
	# Calcular ausencias para diputados con participación significativa
	# Ausencias = total_votaciones - total_votes (votos efectivos)
	df_analisis_filtrado['ausencias'] = total_votaciones - df_analisis_filtrado['total_votes']
	df_analisis_filtrado['porcentaje_ausencias'] = (df_analisis_filtrado['ausencias'] / total_votaciones * 100).round(1)
	
	# TOP 10 diputados con más ausencias
	top_10_ausentes = df_analisis_filtrado.nlargest(10, 'ausencias')
	
	st.caption(f"📊 Ranking de ausencias basado en diputados con al menos {umbral_minimo_votos} votaciones")
	
	# Mostrar el ranking en una tabla más compacta
	st.subheader("👻 TOP 10 - Diputados con Más Ausencias")
	
	for i, diputado in enumerate(top_10_ausentes.itertuples(), 1):
		# Crear contenedor con color de fondo ligeramente diferente para cada fila
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
						{diputado.ausencias} ausencias
					</div>
					<div style="color: #6c757d;">
						{diputado.porcentaje_ausencias:.1f}% del total
					</div>
					<div style="color: #6c757d; font-size: 12px;">
						Participó en {diputado.total_votes}/{total_votaciones} votaciones
					</div>
				</div>
			</div>
		</div>
		"""
		st.markdown(container_html, unsafe_allow_html=True)
	
	# Estadísticas generales de ausencias
	col1, col2, col3 = st.columns(3)
	
	with col1:
		promedio_ausencias = df_analisis_filtrado['ausencias'].mean()
		st.metric(
			label="Promedio de Ausencias", 
			value=f"{promedio_ausencias:.1f}"
		)
	
	with col2:
		porcentaje_promedio_ausencias = df_analisis_filtrado['porcentaje_ausencias'].mean()
		st.metric(
			label="% Promedio de Ausencias", 
			value=f"{porcentaje_promedio_ausencias:.1f}%"
		)
	
	with col3:
		diputado_mas_ausente = top_10_ausentes.iloc[0]
		st.metric(
			label="Máximo de Ausencias", 
			value=f"{diputado_mas_ausente.ausencias} ({diputado_mas_ausente.porcentaje_ausencias:.1f}%)"
		)
	
	st.divider()
	
	# Información adicional
	st.markdown("""
	**Análisis General:** Explora estadísticas detalladas de lealtad partidaria y 
	comportamiento de votación de todos los diputados.

	**Predicciones:** Descubre qué diputados tienen mayor precisión prediciendo 
	los resultados finales de las votaciones.
	""")

def show_analysis():
    """Muestra la página de análisis general (código actual)"""
    # Botón para volver al inicio
    if st.button("← Volver al inicio"):
        st.session_state.page = 'home'
        st.rerun()
    
    # Cargar datos
    df_analisis = load_analysis_data()
    
    # Barra lateral con filtros
    st.sidebar.header("Filtros")
    
    # Crear lista de bloques únicos
    lista_bloques = ['Todos los Bloques'] + sorted(df_analisis['block'].unique().tolist())
    
    # Menu desplegable
    bloque_seleccionado = st.sidebar.selectbox(
        "Seleccionar un Bloque:",
        lista_bloques
    )
    
    # Filtrar DataFrame
    if bloque_seleccionado == 'Todos los Bloques':
        df_filtrado = df_analisis
    else:
        df_filtrado = df_analisis[df_analisis['block'] == bloque_seleccionado]
    
    # Ordenar resultados
    sorted_df = df_filtrado.sort_values(by='average_loyalty', ascending=False)
    
    # Mostrar resultados
    st.title("📊 Análisis de Cohesión Legislativa")
    st.header(f"Análisis para: {bloque_seleccionado}")
    st.write("---")
    
    if sorted_df.empty:
        st.warning("No hay datos para la selección actual.")
    else:
        # Mostrar estadísticas generales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Diputados", len(sorted_df['deputy'].unique()))
        with col2:
            st.metric("Lealtad Promedio", f"{sorted_df['average_loyalty'].mean():.1%}")
        with col3:
            st.metric("Apoyo Oficialismo Promedio", f"{sorted_df['officialism_support'].mean():.1%}")
        
        st.write("---")
        
        # Iterar sobre cada diputado
        for diputado in sorted_df.itertuples():
            # Diseño de la fila principal
            col_info, col_stats = st.columns([1, 2])
            
            # Columna izquierda: Nombre y bloque
            with col_info:
                st.subheader(diputado.deputy)
                st.caption(f"Bloque: {diputado.block}")
            
            # Columna derecha: Estadísticas
            with col_stats:
                st.write("**Estadísticas de votación**")
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                
                with stat_col1:
                    st.metric(label="Lealtad Promedio", value=f"{diputado.average_loyalty:.1%}")
                
                with stat_col2:
                    st.metric(label="Votos Emitidos", value=diputado.total_votes)
                
                with stat_col3:
                    st.metric(label="Apoyo al Oficialismo", value=f"{diputado.officialism_support:.1%}")
            
            st.divider()

def show_predictions():
    """Muestra la página de predicciones con los top 10 diputados"""
    # Botón para volver al inicio
    if st.button("← Volver al inicio"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.title("🎯 Predicciones Legislativas")
    st.header("Top 10 Diputados con Mayor Precisión Predictiva")
    
    st.markdown("""
    Estos son los diputados que más aciertos tienen al predecir el resultado final 
    de las votaciones basándose en su historial de votos.
    """)
    
    # Cargar datos de predicciones
    top_predictors = calculate_prediction_accuracy()
    
    st.write("---")
    
    # Mostrar cada diputado del top 10
    for i, diputado in enumerate(top_predictors.itertuples(), 1):
        # Contenedor con borde para cada diputado
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


if st.session_state.page == 'home':
    show_home()
elif st.session_state.page == 'analysis':
    show_analysis()
elif st.session_state.page == 'predictions':
    show_predictions()