"""
Legislative Analyzer - Streamlit Application

This application provides analysis of Argentine legislative voting patterns,
including deputy loyalty, block cohesion, and attendance tracking.
"""

import streamlit as st
from src.views.dashboard import show_home
from views.deputies import show_analysis_page
from src.views.predictions import show_predictions

# Configure Streamlit page
st.set_page_config(
	layout="wide", 
	page_title="Análisis Legislativo",
	page_icon="🏛️",
	initial_sidebar_state="collapsed"
)

# Initialize session state for navigation
if 'page' not in st.session_state:
	st.session_state.page = 'home'
	
if 'sidebar_state' not in st.session_state:
	st.session_state.sidebar_state = 'collapsed'
	
def set_page(page_name):
	st.session_state.page = page_name

with st.sidebar:
	st.title("Navegación")
	
	st.button("Inicio", on_click=set_page, args=('home',), use_container_width=True)
	st.button("Diputados", on_click=set_page, args=('analysis',), use_container_width=True)
	# st.button("Predicciones", on_click=set_page, args=('predictions',), use_container_width=True)
	
	st.info("Seleccione una sección para explorar diferentes aspectos del análisis legislativo.")

# Main navigation logic
if st.session_state.page == 'home':
	show_home()
elif st.session_state.page == 'analysis':
	show_analysis_page()
# elif st.session_state.page == 'predictions':
	# show_predictions()