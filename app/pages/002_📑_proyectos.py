import streamlit as st
import random, datetime
from yaml import safe_load
import auth

from models import Application
from utils import show_app_state, phases_template


st.set_page_config("Proyectos UH - Proyectos", page_icon="📑", layout="wide")
user = auth.authenticate()

st.header('📑 Proyectos')


if st.session_state.role != "Dirección de Proyecto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Dirección de Proyecto**.")
    st.stop()

phases, phase, conv, period = phases_template()

applications = Application.load_from(program=st.session_state.program, user=st.session_state.user, phase=phase, period=period)
st.info(f"Usted tiene **{len(applications)}** proyectos enviados.")

if not applications:
    st.stop()
app: Application = applications[st.selectbox("Seleccione un proyecto", applications)]
app.save()

show_app_state(app)


def delete_application():
    app.destroy()
    st.session_state['delete-app'] = False
    st.warning(f"⚠️ Proyecto **{app.title}** eliminada satisfactoriamente.")


with st.expander("🔴 BORRAR PROYECTO"):
    st.warning(f"⚠️ La acción siguiente es permanente, todos los datos del proyecto **{app.title}** se perderán.")

    if st.checkbox(f"Soy conciente de que perderé todos los datos del proyecto **{app.title}**.", key="delete-app"):
        st.button("🔴 Eliminar Proyecto", on_click=delete_application)
