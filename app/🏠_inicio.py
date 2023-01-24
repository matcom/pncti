import streamlit as st
import auth

st.set_page_config("PNCTI (Demo)", page_icon="🏠", layout="wide")

user = auth.authenticate()

with open("/src/data/inicio.md") as fp:
    st.write(fp.read().format(user=user, role=st.session_state.role, program=st.session_state.program))
