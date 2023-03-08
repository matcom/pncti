import streamlit as st
import auth
import os


st.set_page_config("Proyectos UH", page_icon="🏠", layout="wide")

user = auth.authenticate()

with open("/src/data/inicio.md") as fp:
    st.write(fp.read().format(user=user, role=st.session_state.role, program=st.session_state.program))


git_version = os.popen("git log -n 1 --pretty='%cd - %h'").readline().strip()
st.info(f"ℹ️ Versión desplegada: **{git_version}**")
