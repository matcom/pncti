import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application, Status
from utils import show_app_state
from tools import send_from_template


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

roles = yaml.safe_load(open("/src/data/roles.yml"))[st.session_state.program]
experts = roles['Experto']

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

def assign_expert(app: Application, i: int, tab):
    "Asignar experto"

    value = tab.selectbox(label="Expertos", options=[f"{name} ({email})" for email, name in experts.items() 
                                                    if email != app.expert_1 and email != app.expert_2],
                         key=f"sb_expert{i}")

    def assign_expert(app, value):
        setattr(app, f'expert_{i}', value.split("(")[-1][:-1])

        app.save()

    tab.button("Asignar experto", on_click=assign_expert, args=(app, value), key=f"b_expert{i}")
    
def unassign_expert(app: Application, i: int):
    "Quitar asignación"
    
    setattr(app, f"expert_{i}", None)
    app.save()

with right:
    st.write(f"#### Evaluación de los expertos")
    
    anexo = config["programs"][app.program]["project_types"][app.project_type]
    name = config["docs"][anexo]["name"]
    file_name = config["docs"][anexo]["file_name"]
    
    tabs = st.tabs(["Experto 1", "Experto 2"])
    for i, tab in enumerate(tabs):
        
        exp = getattr(app, f"expert_{i+1}")
        if exp not in experts.keys():
            tab.warning("No está asignado", icon="⚠️")
            assign_expert(app, i+1, tab)
           
        else:
            tab.write(f"**Nombre:** {experts[exp]}")
        
            exp_file = app.file(file_name=file_name, expert=exp)
            if exp_file:
                tab.download_button(
                    f"⏬ Descargar última versión subida del {name}", exp_file, file_name=file_name
                )
            else:
                tab.warning("No hay evaluación de este experto", icon="⚠️")
                
            with tab.expander("Enviar correo"):
                email = st.form(key=f"expert_email{i}", clear_on_submit=True)
                email.caption(f"A: {exp}")
                message = email.text_area("Mensaje")
                attached = email.file_uploader("Adjuntar archivos", accept_multiple_files=True)
                submited = email.form_submit_button(label="Enviar")
                if submited:
                    send_from_template("program", exp, 
                                       message=message, 
                                       program=st.session_state.program, 
                                       user=roles["Dirección de Programa"][st.session_state.user])
                    
            tab.button(label="⛔ Quitar asignación", on_click=unassign_expert, args=[app, i+1], key=f"u_expert{i}")


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


actions = { func.__doc__: func for func in [review_docs]}

with left:
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
