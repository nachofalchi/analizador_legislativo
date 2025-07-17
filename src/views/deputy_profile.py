import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_deputy_profile(deputy_name: str, full_df: pd.DataFrame):
    """
    Renders the detailed profile page for a specific deputy.
    """

    if st.button("Volver a la lista de diputados"):
        st.session_state.selected_deputy = None
        st.rerun()
        
    st.title(f"{deputy_name}")

    deputy_data = full_df[full_df['deputy'] == deputy_name].iloc[0]

    st.divider()
    st.caption(f"Bloque: {deputy_data.block}")
    
    # Key Metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Lealtad Promedio", f"{deputy_data.average_loyalty:.1%}")
    metric_col2.metric("Votos Emitidos", int(deputy_data.total_votes))
    metric_col3.metric("Apoyo al Oficialismo", f"{deputy_data.officialism_support:.1%}")

    st.divider()
    
    # Desglose del Voto - Gráfico de torta
    st.subheader("Desglose de Votaciones")
    
    # Crear datos para el gráfico de torta
    # Calculamos los valores específicos para afirmativos y negativos si es posible
    # Si no tenemos esa información, usamos una estimación basada en officialism_support
    
    # Estimación de votos afirmativos y negativos basada en apoyo al oficialismo
    votos_afirmativos = int(deputy_data.total_votes * deputy_data.officialism_support)
    votos_negativos = int(deputy_data.total_votes - votos_afirmativos)
    
    # Datos para el gráfico de torta
    categorias = ['Afirmativo', 'Negativo', 'Ausente', 'Sin Votar', 'Abstención']
    valores = [
        votos_afirmativos, 
        votos_negativos,
        int(deputy_data.absent),
        int(deputy_data.not_voted),
        int(deputy_data.abstention)
    ]
    
    # Colores para cada categoría
    colores = {
        'Afirmativo': '#4CAF50', 
        'Negativo': '#F44336',
        'Ausente': '#9E9E9E', 
        'Sin Votar': '#607D8B',
        'Abstención': '#FF9800'
    }
    
    # Calcular el total para los porcentajes
    total_participaciones = sum(valores)
    
    # Crear el gráfico solo si hay datos
    if total_participaciones > 0:
        # Crear un dataframe para el gráfico
        df_pie = pd.DataFrame({
            'Categoría': categorias,
            'Cantidad': valores
        })
        
        # Filtrar categorías con valor 0
        df_pie = df_pie[df_pie['Cantidad'] > 0]
        
        # Crear el gráfico de torta
        fig = px.pie(
            df_pie, 
            values='Cantidad', 
            names='Categoría',
            color='Categoría',
            color_discrete_map=colores,
        )
        
        # Personalizar el gráfico
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}'
        )
        
        fig.update_layout(
            legend_title="Tipo de Voto",
            title={
                'text': "",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 20}
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("No hay datos de votaciones disponibles para este diputado.")
    
    st.divider()
    
    # st.subheader("Análisis Detallado")
    # Placeholder for more detailed charts for this specific deputy
    # st.info("Aquí podrías mostrar un historial de votos clave, un radar de afinidad, etc.")