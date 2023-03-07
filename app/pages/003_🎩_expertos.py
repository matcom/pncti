import streamlit as st
import auth

st.set_page_config(page_title="Proyectos UH - Expertos", page_icon="🎩", layout="wide")
user = auth.authenticate()

st.header('🎩 Expertos')


if st.session_state.role != "Experto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Experto**.")
    st.stop()
