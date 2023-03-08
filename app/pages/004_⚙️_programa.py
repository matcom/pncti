import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application
from utils import show_app_state


st.set_page_config(page_title="Proyectos UH - Programa", page_icon="⚙️", layout="wide")
user = auth.authenticate()

st.header("⚙️ Gestión del Programa")


if st.session_state.role != "Dirección de Programa":
    st.warning(
        "⚠️ Esta sección solo está disponible para el rol de **Dirección de Programa**."
    )
    st.stop()

applications = list(Application.load_from(program=st.session_state.program))
df = []
experts = yaml.safe_load(open("/src/data/roles.yml"))[st.session_state.program]['Experto']

if not applications:
    st.warning(
        "⚠️ No hay aplicaciones registradas en el programa."
    )
    st.stop()
    
for app in applications:
    df.append(
        dict(
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            Experto1=experts[app.expert_1] if app.expert_1 else "",
            Experto2=experts[app.expert_2] if app.expert_2 else "",
        )
    )

df = pd.DataFrame(df).set_index("Título")

st.write("### Resumen de aplicaciones")
st.write(df)

app = st.selectbox(
    "Seleccione una aplicación", applications, format_func=lambda app: app.title
)

if app is None:
    st.stop()

left, right = show_app_state(app)

def assign_expert(app):
    "Asignar experto"

    value = st.multiselect(label="Expertos", options=[f"{exp[1]} ({exp[0]})" for exp in experts.items()], max_selections=2)
    
    if st.button("Asignar expertos"):
        for i, expert in enumerate(value):
            exec(f'app.expert_{i+1} = str(expert).split("(")[1][:-1]')
        app.save()

def review_docs(app):
    "Revisión inicial de documentos"

    value = st.selectbox("Dictamen", ["Aceptar", "Rechazar"])

    if st.button("Aplicar dictamen"):
        if value == "Aceptar":
            pass


actions = [assign_expert]

with right:
    st.write("### Acciones")

    action = st.selectbox("Seleccione una opción", actions, format_func=lambda func: func.__doc__)
    action(app)
