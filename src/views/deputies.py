# src/views/deputies.py

import streamlit as st
import pandas as pd
from src.data_loader import load_analysis_data
from src.views.deputy_profile import show_deputy_profile

ITEMS_PER_PAGE = 20  # Number of deputies to show per page

def initialize_state():
    """Initializes all session state variables for this view if they don't exist."""
    if 'block_filter' not in st.session_state:
        st.session_state.block_filter = 'All Blocks'
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ''
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
    if 'selected_deputy' not in st.session_state:
        st.session_state.selected_deputy = None

def reset_pagination():
    """Callback function to reset the page number when a filter changes."""
    st.session_state.page_number = 1

def show_deputies_list(analysis_df: pd.DataFrame):
    """
    Displays the main list of deputies with filtering, searching, and pagination.
    """
    st.header("Análisis por Diputado")
    st.write("Utilice los filtros para explorar el comportamiento de los legisladores.")

    # --- RENDER FILTERS ---
    block_list = ['All Blocks'] + sorted(analysis_df['block'].unique().tolist())
    filter_col1, filter_col2 = st.columns([1, 2])
    
    with filter_col1:
        st.selectbox("Filtrar por Bloque:", block_list, key='block_filter', on_change=reset_pagination)
    
    with filter_col2:
        st.text_input("Buscar Diputado:", key='search_term', on_change=reset_pagination)

    # --- APPLY FILTERS ---
    filtered_df = analysis_df
    if st.session_state.block_filter != 'All Blocks':
        filtered_df = filtered_df[filtered_df['block'] == st.session_state.block_filter]
    if st.session_state.search_term:
        filtered_df = filtered_df[filtered_df['deputy'].str.contains(st.session_state.search_term, case=False)]

    sorted_df = filtered_df.sort_values(by='average_loyalty', ascending=False)
    st.divider()

    # --- RENDER SUMMARY METRICS ---
    if sorted_df.empty:
        st.warning("No se encontraron diputados con los filtros seleccionados.")
        return

    st.subheader(f"Resultados para: {st.session_state.block_filter}")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Total Diputados Encontrados", len(sorted_df['deputy'].unique()))
    metric_col2.metric("Lealtad Promedio del Grupo", f"{sorted_df['average_loyalty'].mean():.1%}")
    metric_col3.metric("Apoyo Promedio al Oficialismo", f"{sorted_df['officialism_support'].mean():.1%}")
    
    st.divider()

    # --- PAGINATION ---
    total_items = len(sorted_df)
    total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE > 0 else 0)
    start_idx = (st.session_state.page_number - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paginated_df = sorted_df.iloc[start_idx:end_idx]

    # --- RENDER PAGINATED LIST ---
    for i, row in enumerate(paginated_df.itertuples()):
        with st.container(border=True):
            col_info, col_button = st.columns([4, 1])
            with col_info:
                st.subheader(row.deputy)
                st.caption(f"Bloque: {row.block} | Lealtad: {row.average_loyalty:.1%}")
            with col_button:
                # Usar una combinación de índice, nombre y bloque para garantizar unicidad
                button_key = f"view_{start_idx + i}_{row.deputy}_{row.block}"
                if st.button("Ver Perfil", key=button_key, use_container_width=True):
                    st.session_state.selected_deputy = row.deputy
                    st.rerun()
    
    # --- PAGINATION CONTROLS ---
    if total_pages > 1:
        st.divider()
        prev_col, page_col, next_col = st.columns([3, 1, 3])
        if st.session_state.page_number > 1:
            if prev_col.button("Anterior", use_container_width=True):
                st.session_state.page_number -= 1
                st.rerun()
        page_col.write(f"Página {st.session_state.page_number} de {total_pages}")
        if st.session_state.page_number < total_pages:
            if next_col.button("Siguiente", use_container_width=True):
                st.session_state.page_number += 1
                st.rerun()

def show_analysis_page():
    """
    Main router for the analysis view. Decides whether to show the
    list of deputies or a specific deputy's profile page.
    """
    initialize_state()
    
    if st.session_state.selected_deputy is None:
        analysis_df = load_analysis_data()
        show_deputies_list(analysis_df)
    else:
        full_df = load_analysis_data()
        show_deputy_profile(st.session_state.selected_deputy, full_df)