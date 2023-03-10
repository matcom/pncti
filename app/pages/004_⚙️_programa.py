import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application, Status
from utils import show_app_state


st.set_page_config(page_title="Proyectos UH - Programa", page_icon="⚙️", layout="wide")
user = auth.authenticate()

st.header("⚙️ Gestión del Programa")

config = yaml.safe_load(open("/src/data/config.yml"))

if st.session_state.role != "Dirección de Programa":
    st.warning(
        "⚠️ Esta sección solo está disponible para el rol de **Dirección de Programa**."
    )
    st.stop()

applications = Application.load_from(program=st.session_state.program)

df = []
experts = yaml.safe_load(open("/src/data/roles.yml"))[st.session_state.program]['Experto']

if not applications:
    st.warning(
        "⚠️ No hay aplicaciones registradas en el programa."
    )
    st.stop()
    
for i, app in enumerate(applications.values()):
    df.append(
        dict(
            No=i+1,
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            Experto1=experts[app.expert_1] if app.expert_1 else "",
            Experto2=experts[app.expert_2] if app.expert_2 else "",
        )
    )

df = pd.DataFrame(df).set_index("No")

with st.expander(f"Listado de aplicaciones ({len(df)})"):
    st.table(df)

app: Application = applications[st.selectbox("Seleccione una aplicación", applications)]

if app is None:
    st.stop()

left, right = show_app_state(app, expert=True)

with right:
    st.write(f"#### Evaluación de los expertos")
    
    anexo = config["programs"][app.program]["project_types"][app.project_type]
    name = config["docs"][anexo]["name"]
    file_name = config["docs"][anexo]["file_name"]
        
    for i in range(1, 3):
        exp = getattr(app, f"expert_{i}")
        st.write(f"**Experto {i}:** {experts[exp] if exp in experts.keys() else 'No está asignado'}")
        
        exp_file = app.file(file_name=file_name, expert=exp)
        if exp_file:
            st.download_button(
                f"⏬ Descargar última versión subida del {name}", exp_file, file_name=file_name
            )
        else:
            st.warning("Este experto no ha subido su evaluación", icon="⚠️")
        

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
