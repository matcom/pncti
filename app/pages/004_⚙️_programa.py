import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application, Status, Expert, Evaluation, Phase
from utils import show_app_state
from tools import send_from_template
from fastapi.encoders import jsonable_encoder


st.set_page_config(page_title="Proyectos UH - Programa", page_icon="⚙️", layout="wide")
user = auth.authenticate()

st.header("⚙️ Gestión del Programa")

config = yaml.safe_load(open("/src/data/config.yml"))
if st.session_state.role != "Dirección de Programa":
    st.warning(
        "⚠️ Esta sección solo está disponible para el rol de **Dirección de Programa**."
    )
    st.stop()

phases = [Phase.announcement, Phase.execution]
phase = st.select_slider("Mostrar proyectos en:", map(lambda x: x.value, phases), value=Phase.execution.value)
applications = Application.load_from(program=st.session_state.program, phase=phase)

df, exp_df = [], []

roles = yaml.safe_load(open("/src/data/roles.yml"))
experts = roles[st.session_state.program]['Experto']
program = config["programs"][st.session_state.program]

if not applications:
    st.warning(
        "⚠️ No hay aplicaciones registradas en esta fase."
    )
    st.stop()
    
for i, app in enumerate(applications.values()):
    exp_table = {key:f"{experts[value.username]} ({value.evaluation.final_score})" if value.username in experts.keys() else "" 
                 for key,value in app.experts.items()}
    exp_scores = {key:f"{value.evaluation.final_score}" if value.username in experts.keys() else "" 
                 for key,value in app.experts.items()}
    exp_table["Total"] = sum([value.evaluation.coeficent * value.evaluation.final_score for key, value in app.experts.items()])
    df.append(
        dict(
            No=i+1,
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            **exp_table,
        )
    )
    exp_df.append(
        dict(
            No=i+1,
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            **exp_scores,
        )
    )
df = pd.DataFrame(df).set_index("No")
exp_df = pd.DataFrame(exp_df).set_index("No")

with st.expander(f"Listado de aplicaciones ({len(df)})"):
    st.table(df)
    df.to_excel(f"{st.session_state.path}/Aplicaciones.xlsx")
    exp_df.to_excel(f"{st.session_state.path}/Puntuaciones.xlsx")
    st.download_button(label="📊 Descargar Tabla", 
                       data=open(f"{st.session_state.path}/Aplicaciones.xlsx", "rb"),
                       file_name="Aplicaciones.xlsx")
    st.download_button(label="⏬ Descargar Puntuaciones", 
                       data=open(f"{st.session_state.path}/Puntuaciones.xlsx", "rb"),
                       file_name="Puntuaciones.xlsx")

app: Application = applications[st.selectbox("Seleccione una aplicación", applications)]

if app is None:
    st.stop()

sections = st.tabs(["General", "Expertos", "Agregar"])

if not app.experts:
    for key, value in program[phase]["experts"].items():
        for i in range(value["number"]):
            app.experts[f"{value['name']} {i+1}"] = Expert(role=key, 
                                                           evaluation=Evaluation(coeficent=program[phase]["project_types"][app.project_type][key]))
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
    
def final_review(app: Application):
    "Revisión final del proyecto"
    
    value = st.selectbox("Dictamen", ["Aceptar", "Rechazar"])

    def final_review(app, value):
        if value == "Aceptar":
            app.phase = Phase.execution
            app.project_type = "Certificación"
            app.experts = {}
        else:
            app.phase = Phase.announcement

        app.save()

    st.button("Aplicar dictamen", on_click=final_review, args=(app, value))

dict_actions = {
    "final_review": final_review,
    "move_app": move_app,
    "review_docs": review_docs
}

current_actions = program[phase]["actions"]
actions = { func[1].__doc__: func[1] for func in dict_actions.items() if func[0] in current_actions}

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
    
    unassign_expert(app, name)
    value = struct.selectbox(label="Expertos", options=[f"{name} ({email})" for email, name in experts.items() 
                                                    if not sum([1 for e in app.experts.values() if e.username == email])],
                         key=f"sb{name.strip()}{app.uuid}")
    expert = value.split("(")[-1][:-1]
    
    def assign_expert(app: Application, value, role):
        app.experts[name].username = expert
        app.experts[name].phase = phase
        
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
    
    app.experts[name].reset()
    app.save()
    
def add_role(role: str, name: str, email: str):
    "Agregar rol"
    
    roles[st.session_state.program][role][email] = name
    with open("/src/data/roles.yml", "w") as role_file:
        yaml.safe_dump(jsonable_encoder(roles), roles_file)
    
def del_role(role: str, email: str):
    "Borrar rol"
    
    del roles[st.session_state.program][role][email]
    with open("/src/data/roles.yml", "w") as roles_file:
        yaml.safe_dump(jsonable_encoder(roles), role_file)
        
def add_project(title: str, owner: str):
    pass
    

with sections[1]:
    st.write(f"#### Evaluación de los expertos")
    anexo = config["programs"][app.program][app.phase.value]["project_types"][app.project_type]["doc"]
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
                       user=roles[st.session_state.program]["Dirección de Programa"][st.session_state.user])
                    
            tab.button(label="⛔ Quitar asignación", on_click=unassign_expert, args=[app, evaluators[i]], key=f"u_expert{i}_{app.uuid}")
    
with sections[2]:
    st.write("#### Agregar experto")
    email = st.text_input("Correo")
    name = st.text_input("Nombre")
    if email and name:
        if st.button("Agregar", on_click=add_role, args=("Experto", name, email)):
            st.success("Experto agregado satisfactoriamente")
            
    st.write("#### Agregar proyecto")
    app_title = st.text_input("Título")
    app_owner = st.text_input("Correo del titular")
    app_phase = st.selectbox("Fase", ["Convocatoria", "Ejecución"])
    app_project_type = None
    if app_phase:
        app_project_type = st.selectbox("Tipo de proyecto", list(program[app_phase]["project_types"].keys()))
    if app_title and app_project_type and app_owner:
        insert = st.button("Crear")
        if insert:
            Application(title = app_title, 
                        project_type = app_project_type, 
                        program = st.session_state.program, 
                        owner = app_owner,
                        path = program["path"],
                        phase = Phase.announcement if app_phase == "Convocatoria" else Phase.execution).create()
            st.success("**🥳 Aplicación agregada satisfactoriamente**")
    else:
        st.warning("⚠️ Faltan datos por instertar")