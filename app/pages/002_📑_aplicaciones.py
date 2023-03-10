import streamlit as st
import random
import auth

from models import Application, Status
from utils import show_app_state


st.set_page_config("Proyectos UH - Aplicaciones", page_icon="馃搼", layout="wide")
user = auth.authenticate()

st.header('馃搼 Aplicaciones')


if st.session_state.role != "Direcci贸n de Proyecto":
    st.warning("鈿狅笍 Esta secci贸n solo est谩 disponible para el rol de **Direcci贸n de Proyecto**.")
    st.stop()

applications = Application.load_from(program=st.session_state.program, user=st.session_state.user)

st.info(f"Usted tiene **{len(applications)}** aplicaciones enviadas.")

app: Application = applications[st.selectbox("Seleccione una aplicaci贸n", applications)]

if not app:
    st.stop()

show_app_state(app)

def delete_application():
    app.destroy()
    st.session_state['delete-app'] = False
    st.warning(f"鈿狅笍 Aplicaci贸n **{app.title}** eliminada satisfactoriamente.")


with st.expander("馃敶 BORRAR APLICACI脫N"):
    st.warning(f"鈿狅笍 La acci贸n siguiente es permanente, todos los datos de la aplicaci贸n **{app.title}** se perder谩n.")

    if st.checkbox(f"Soy conciente de que perder茅 todos los datos de la aplicaci贸n **{app.title}**.", key="delete-app"):
        st.button("馃敶 Eliminar Aplicaci贸n", on_click=delete_application)
