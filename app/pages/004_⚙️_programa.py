import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application, Status, Expert, Evaluation
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
program = config["programs"][st.session_state.program]

if not applications:
    st.warning(
        "⚠️ No hay aplicaciones registradas en el programa."
    )
    st.stop()
    
for i, app in enumerate(applications.values()):
    exp_table = {key:experts[value.username] if value.username else "" for key,value in app.experts.items() if value.role == "regular"}
    df.append(
        dict(
            No=i+1,
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            **exp_table
        )
    )

df = pd.DataFrame(df).set_index("No")

with st.expander(f"Listado de aplicaciones ({len(df)})"):
    st.table(df)
    df.to_excel(f"{st.session_state.path}/Aplicaciones.xlsx")
    st.download_button(label="⏬ Descargar Tabla", 
                       data=open(f"{st.session_state.path}/Aplicaciones.xlsx", "rb"),
                       file_name="Aplicaciones.xlsx")

app: Application = applications[st.selectbox("Seleccione una aplicación", applications)]

if app is None:
    st.stop()

sections = st.tabs(["General", "Expertos"])

if not app.experts:
    for key, value in program["experts"].items():
        for i in range(value["number"]):
            app.experts[f"{value['name']} {i+1}"] = Expert(role=key, 
                                                           evaluation=Evaluation(coeficent=program["project_types"][app.project_type][key]))
    app.save()


def email_form(struct, template, to_email, key, **kwargs):
    with struct.expander("📧 Enviar correo"):
        email = st.form(key=f"email_{key}", clear_on_submit=True)
        email.caption(f"A: {to_email}")
        message = email.text_area("Mensaje")
        kwargs["message"] = message
        submited = email.form_submit_button(label="Enviar")
        if submited:
            send_from_template(template, to_email, **kwargs)    

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
    
    email_form(st, "notify", app.owner, f"reject{app.uuid}",
               application=app.title,
               program=app.program)
    
def move_app(app: Application):
    "Mover aplicación a otro programa"
    
    value = st.selectbox("Programa", [prog for prog in config["programs"] if prog != app.program])
    
    def move_app(app, value):
        new_path = config["programs"][value]["path"]
        app.move(old_program=app.program, new_program=value, new_path=new_path)
        app.save()
    
    st.info(f"Usted va a mover la aplicación {app.title} al programa {value}", icon="ℹ️")
    st.button("Mover", on_click=move_app, args=[app, value])    

actions = { func.__doc__: func for func in [review_docs, move_app]}

def delete_application():
    app.destroy()
    st.session_state['delete-app'] = False
    st.warning(f"⚠️ Aplicación **{app.title}** eliminada satisfactoriamente.")

with sections[0]:
    left, right = show_app_state(app, expert=False)
    
    with left:
        st.write("#### Acciones")
        action = st.selectbox("Seleccione una opción", actions)
        actions[action](app)
    with st.expander("🔴 BORRAR APLICACIÓN"):
        st.warning(f"⚠️ La acción siguiente es permanente, todos los datos de la aplicación **{app.title}** se perderán.")

        if st.checkbox(f"Soy conciente de que perderé todos los datos de la aplicación **{app.title}**.", key="delete-app"):
            st.button("🔴 Eliminar Aplicación", on_click=delete_application)

def assign_expert(app: Application, name: str, role: str, struct):
    "Asignar experto"

    value = struct.selectbox(label="Expertos", options=[f"{name} ({email})" for email, name in experts.items() 
                                                    if not sum([1 for e in app.experts.values() if e.username == email])],
                         key=f"sb{name.strip()}{app.uuid}")
    expert = value.split("(")[-1][:-1]
    
    def assign_expert(app: Application, value, role):
        app.experts[name].username = expert
        
        send_from_template("expert_notify", expert, 
                           user=experts[expert],
                           application=app.title,
                           proj_type=app.project_type,
                           program=st.session_state.program,
                           )
        app.experts[name].notify = True
        app.save()
        
                
    assign = struct.button("🎩 Asignar experto", on_click=assign_expert, args=(app, value, role), key=f"b{name.strip()}{app.uuid}")
    
def unassign_expert(app: Application, name: str):
    "Quitar asignación"
    
    app.experts[name].username = None
    app.experts[name].notify = False
    app.save()

with sections[1]:    
    st.write(f"#### Evaluación de los expertos")
    
    anexo = config["programs"][app.program]["project_types"][app.project_type]["doc"]
    name = config["docs"][anexo]["name"]
    file_name = config["docs"][anexo]["file_name"]

    evaluators = list(app.experts.keys())
    tabs = st.tabs(evaluators)
    
    for i, tab in enumerate(tabs):
        exp = app.experts[evaluators[i]]
        count = sum([1 for app in applications.values() if exp.username in [e.username for e in app.experts.values()]])
        if exp.username not in experts.keys():
            tab.warning("No está asignado", icon="⚠️")
            assign_expert(app, evaluators[i], exp.role, tab)
           
        else:
            tab.write(f"**Nombre:** {experts[exp.username]} ({count})")
        
            exp_file = app.file(file_name=file_name, expert=exp.username)
            if exp_file:
                tab.download_button(
                    f"⏬ Descargar última versión subida del {name}", exp_file, file_name=file_name
                )
            else:
                tab.warning("No hay evaluación de este experto", icon="⚠️")
            
            if exp.notify:
                tab.info("El experto fue notificado", icon="ℹ️")
                
            email_form(tab, "program", exp.username, f"expert_{i}",
                       program=st.session_state.program, 
                       user=roles["Dirección de Programa"][st.session_state.user])
                    
            tab.button(label="⛔ Quitar asignación", on_click=unassign_expert, args=[app, evaluators[i]], key=f"u_expert{i}_{app.uuid}")
