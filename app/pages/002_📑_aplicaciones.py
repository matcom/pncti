import streamlit as st
import random
import auth

from models import Application, Status
from utils import show_app_state


st.set_page_config("PNCTI (Demo) - Aplicaciones", page_icon="📑", layout="wide")
user = auth.authenticate()

st.header('📑 Aplicaciones')


if st.session_state.role != "Dirección de Proyecto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Dirección de Proyecto**.")
    st.stop()

applications = list(Application.load_from(program=st.session_state.program, user=st.session_state.user))

st.info(f"Usted tiene **{len(applications)}** aplicaciones enviadas.")

app: Application = st.selectbox("Seleccione una aplicación", applications, format_func=lambda app: app.title)

if not app:
    st.stop()

show_app_state(app)
