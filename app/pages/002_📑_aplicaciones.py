import streamlit as st
import random
import auth

from models import Application


st.set_page_config("PNCTI (Demo) - Aplicaciones", page_icon="📑", layout="wide")

st.header('📑 Aplicaciones')

user = auth.authenticate()

if st.session_state.role != "Dirección de Proyecto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Dirección de Proyecto**.")
    st.stop()

applications = list(Application.load_from(user=st.session_state.user))

st.info(f"Usted tiene **{len(applications)}** aplicaciones enviadas.")

app = st.selectbox("Seleccione una aplicación", applications, format_func=lambda app: app.title)

if not app:
    st.stop()

st.write(f"### {app.title} - {app.project_type}")

st.write(f"#### Documentación de la aplicación")

st.download_button("🔽 Descargar Anexo 3", app.file("Anexo3.docx").read(), "Anexo3.docx")
st.download_button("🔽 Descargar Aval del CC", app.file("AvalCC.docx").read(), "AvalCC.docx")
st.download_button("🔽 Descargar Presupuesto", app.file("Presupuesto.xlsx").read(), "Presupuesto.xlsx")

st.write("#### Estado de la aplicación")
