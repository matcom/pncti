import streamlit as st
import auth

st.set_page_config(page_title="PNCTI (Demo) - Expertos", page_icon="🎩", layout="wide")

st.header('🎩 Expertos')

user = auth.authenticate()

if st.session_state.role != "Experto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Experto**.")
    st.stop()
