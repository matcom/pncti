import streamlit as st
import auth

st.set_page_config("PNCTI (Demo)", page_icon="🏠", layout="wide")

user = auth.authenticate()
