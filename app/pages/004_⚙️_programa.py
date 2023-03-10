import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application, Status
from utils import show_app_state


st.set_page_config(page_title="Proyectos UH - Programa", page_icon="⚙️", layout="wide")
user = auth.authenticate()

st.header("⚙️ Gestión del Programa")


if st.session_state.role != "Dirección de Programa":
    st.warning(
        "⚠️ Esta sección solo está disponible para el rol de **Dirección de Programa**."
    )
    st.stop()

applications = Application.load_from(program=st.session_state.program, user=st.session_state.user)

df = []
experts = yaml.safe_load(open("/src/data/roles.yml"))[st.session_state.program]['Experto']

if not applications:
    st.warning(
        "⚠️ No hay aplicaciones registradas en el programa."
    )
    st.stop()

for app in applications.values():
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

with st.expander(f"Listado de aplicaciones ({len(df)})"):
    st.table(df)

app: Application = applications[st.selectbox("Seleccione una aplicación", applications)]

if app is None:
    st.stop()

left, right = show_app_state(app, expert=True)

def assign_expert(app: Application):
    "Asignar experto"

    value = st.multiselect(label="Expertos", options=[f"{name} ({email})" for email, name in experts.items()], max_selections=2)

    def assign_expert(app, value):
        for i, expert in enumerate(value):
            setattr(app, f'expert_{i+1}', str(expert).split("(")[1][:-1])

        app.save()

    st.button("Asignar expertos", on_click=assign_expert, args=(app, value))


def review_docs(app: Application):
    "Revisión inicial de documentos"

    value = st.selectbox("Dictamen", ["Aceptar", "Rechazar"])

    def review_doc(app, value):
        if value == "Aceptar":
            app.doc_review = Status.accept
        else:
            app.doc_review = Status.reject

        app.save()

    st.button("Aplicar dictamen", on_click=review_doc, args=(app, value))


actions = { func.__doc__: func for func in [review_docs, assign_expert]}

with right:
    st.write("#### Acciones")

    action = st.selectbox("Seleccione una opción", actions)
    actions[action](app)


def delete_application():
    app.destroy()
    st.session_state['delete-app'] = False
    st.warning(f"⚠️ Aplicación **{app.title}** eliminada satisfactoriamente.")


with st.expander("🔴 BORRAR APLICACIÓN"):
    st.warning(f"⚠️ La acción siguiente es permanente, todos los datos de la aplicación **{app.title}** se perderán.")

    if st.checkbox(f"Soy conciente de que perderé todos los datos de la aplicación **{app.title}**.", key="delete-app"):
        st.button("🔴 Eliminar Aplicación", on_click=delete_application)
