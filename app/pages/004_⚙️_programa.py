import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application
from utils import show_app_state


st.set_page_config(page_title="PNCTI (Demo) - Programa", page_icon="⚙️", layout="wide")
user = auth.authenticate()

st.header("⚙️ Gestión del Programa")


if st.session_state.role != "Dirección de Programa":
    st.warning(
        "⚠️ Esta sección solo está disponible para el rol de **Dirección de Programa**."
    )
    st.stop()

applications = list(Application.load_from(program=st.session_state.program))
df = []

for app in applications:
    df.append(
        dict(
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            Experto1=app.expert_1 or "",
            Experto2=app.expert_2 or "",
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
    "Assignar experto"


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
