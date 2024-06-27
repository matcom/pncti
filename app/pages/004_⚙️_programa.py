from logging import disable
import pandas as pd
import streamlit as st
import yaml
import auth

from models import Application, Status, Expert, Evaluation, Phase
from utils import show_app_state, phases_template
from tools import send_from_template
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Proyectos UH - Programa", page_icon="⚙️", layout="wide")
user = auth.authenticate()

st.header("⚙️ Gestión del Programa")

config = yaml.safe_load(open("/src/data/config.yml"))
if st.session_state.role != "Dirección de Programa":
    st.warning(
        "⚠️ Esta sección solo está disponible para el rol de **Dirección de Programa**."
    )
    st.stop()

phases, phase, conv, period = phases_template()

applications = Application.load_from(program=st.session_state.program, phase=phase, period=period)

df, exp_df = [], []

roles = yaml.safe_load(open("/src/data/roles.yml"))
experts = roles[st.session_state.program]['Experto']
program = config["programs"][st.session_state.program]

if not applications:
    st.warning(
        "⚠️ No hay proyectos registrados en esta fase."
    )
    st.stop()
    
for i, app in enumerate(sorted(applications.values(), key=lambda x: x.code)):
    exp_table = {key:f"{experts[value.username]} {'('+str(value.evaluation.final_score)+')' if phase != 'Ejecución' else ''}" 
            if value.username in experts.keys() else "" 
                 for key,value in app.experts.items()}
    exp_scores = {key:f"{value.evaluation.final_score}" if value.username in experts.keys() else "" 
                 for key,value in app.experts.items()}
    if phase == "Convocatoria":
        exp_table["Total"] = sum([value.evaluation.coeficent * value.evaluation.final_score for key, value in app.experts.items()])
    df.append(
        dict(
            No=i+1 if phase != 'Ejecución' else app.code,
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            **exp_table,
        )
    )
    exp_df.append(
        dict(
            No=i+1 if phase == 'Ejecución' else app.code,
            Título=app.title,
            Tipo=app.project_type,
            Jefe=app.owner,
            **exp_scores,
        )
    )
df = pd.DataFrame(df).set_index("No")
exp_df = pd.DataFrame(exp_df).set_index("No")

with st.expander(f"Listado de proyectos ({len(df)})"):
    st.table(df)
    df.to_excel(f"{st.session_state.path}/Aplicaciones.xlsx")
    exp_df.to_excel(f"{st.session_state.path}/Puntuaciones.xlsx")
    st.download_button(label="📊 Descargar Tabla", 
                       data=open(f"{st.session_state.path}/Aplicaciones.xlsx", "rb"),
                       file_name="Aplicaciones.xlsx")
    st.download_button(label="⏬ Descargar Puntuaciones", 
                       data=open(f"{st.session_state.path}/Puntuaciones.xlsx", "rb"),
                       file_name="Puntuaciones.xlsx")

app: Application = applications[st.selectbox("Seleccione un proyecto", applications)]

if app is None:
    st.stop()

sections = st.tabs(["General", "Expertos", "Gestión"])

if not app.experts:
    for key, value in program[phase]["experts"].items():
        for i in range(value["number"]):
            app.experts[f"{value['name']} {i+1}"] = Expert(role=key, 
                                                           evaluation=Evaluation(coeficent=program[phase]["project_types"][app.project_type][key]))
    app.save()
     

class checker:
    @staticmethod
    def check_apps(program: str) -> None:
        structure = yaml.safe_load(open("/src/data/config.yml"))["structure"]
        program_folder = Path(f"/src/data/programs/{program}")
        for file in (program_folder/"applications").glob("*.yml"):
            Application(**yaml.safe_load(file.open())).save()
            app = yaml.safe_load(file.open())
            # checker._check_fields(structure=structure, app=app)
            checker._check_period(app=app)
            # checker._check_phase(app=app)

            yaml.safe_dump(app, file.open(mode='w'))
    @staticmethod         
    def _check_fields(structure: str, app: dict) -> dict:
        fields = []
        for field in app:
            if field not in structure:
                fields.append(field)
        for field in fields:
            del app[field]
        return app
    
    @staticmethod         
    def _check_period(app: dict) -> dict:
        phase: str = app["phase"]
        period: tuple = app["period"]
        if phase == "Ejecución" and not (period[0] <= datetime.now().year <= period[1]):
            app["period"] = (2021,2023)
        return app

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
    "Mover proyecto a otro programa"
    
    value = st.selectbox("Programa", [prog for prog in config["programs"] if prog != app.program])
    
    def move_app(app, value):
        new_path = config["programs"][value]["path"]
        app.move(old_program=app.program, new_program=value, new_path=new_path)
        app.save()
    
    st.info(f"Usted va a mover el proyecto {app.title} al programa {value}", icon="ℹ️")
    st.button("Mover", on_click=move_app, args=[app, value])  

def final_review(app: Application) -> None:
    "Revisión final del proyecto"
    
    value = st.selectbox("Dictamen", ["Seleccionado", "Aprobado", "No Aprobado"])

    def final_review(app, value):
        if value == "Seleccionado":
            app.phase = Phase.execution
            app.project_type = "Certificación"
            app.overal_review = Status.selected
            # app.period = (datetime.now().year + 1, datetime.now().year + 3)
            app.experts = {}
        elif value == "Aprobado":
            app.overal_review = Status.aproved
        elif value == "No Aprobado":
            app.overal_review = Status.not_aproved
            # app.phase = Phase.announcement

        app.save()

    st.button("Aplicar dictamen", on_click=final_review, args=(app, value))
    
def finished_app(app: Application) -> None:
    "Cerrar proyecto"
    
    def finished_app(app):
        app.phase = Phase.finished
        app.project_type = "Finalizado"
        app.overal_review = Status.end
        app.experts = {}
        app.save()
    st.info(f"Usted va a cerrar el proyecto {app.title}", icon="ℹ️")
    st.button("Cerrar", on_click=finished_app, args=[app])

def nothing(app: Application) -> None:
    "Nada para hacer ..."
    return

dict_actions = {
    "final_review": final_review,
    "finished_app": finished_app,
    "move_app": move_app,
    "review_docs": review_docs,
    "nothing": nothing
}

current_actions = program[phase]["actions"]
actions = { func.__doc__: func for action, func in dict_actions.items() if action in current_actions}

def delete_application():
    app.destroy()
    st.session_state['delete-app'] = False
    st.warning(f"⚠️ Proyecto **{app.title}** eliminada satisfactoriamente.")

with sections[0]:
    left, right = show_app_state(app, expert=False)
    
    with left:
        st.write("#### Acciones")
        action = st.selectbox("Seleccione una opción", actions)
        actions[action](app)
    
    with st.expander("🔴 BORRAR PROYECTO"):
        st.warning(f"⚠️ La acción siguiente es permanente, todos los datos del proyecto **{app.title}** se perderán.")

        if st.checkbox(f"Soy conciente de que perderé todos los datos del proyecto **{app.title}**.", key="delete-app"):
            st.button("🔴 Eliminar Proyecto", on_click=delete_application)

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
    
def add_user():
    "Agregar usuario"
    
    def add_user(role, name, email):
        roles[st.session_state.program][value][email] = name
        with open("/src/data/roles.yml", "w") as role_file:
            yaml.safe_dump(jsonable_encoder(roles), role_file)
        st.success(f"✅ {value} agregado correctamente")
    
    value = st.selectbox("Rol", list(roles[st.session_state.program].keys()))
    email = st.text_input("Correo")
    name = st.text_input("Nombre")
    button = st.button("Agregar", on_click=add_user, args=(value, name, email), disabled=not (email and name and value))

def del_user():
    "Borrar usuario"
    
    role = st.selectbox("Rol", [""]+list(roles[st.session_state.program].keys()), key=f"role{st.session_state.user}")
    value = st.selectbox(label="Usuario", options=[f"{name} ({email})" for email, name in 
                                                    roles[st.session_state.program][role].items()] if role else [],
                            key=f"email{st.session_state.user}")
    email = value.split("(")[-1][:-1] if value else ""
    
    def del_user(email):
        del roles[st.session_state.program][role][email]
        with open("/src/data/roles.yml", "w") as roles_file:
            yaml.safe_dump(jsonable_encoder(roles), roles_file)
        st.success(f"✅ {email} eliminado correctamente")
    
    button = st.button("Borrar", on_click=del_user, args=(email,), disabled=not (role and value))

def add_project():
    "Agregar proyecto"
    
    def add_project(title, owner, phase, project_type, institution, code):
        app = Application(title = title, 
                        project_type = project_type, 
                        program = st.session_state.program, 
                        owner = owner,
                        institution = institution,
                        code = code,
                        path = program["path"],
                        phase = Phase.announcement if phase == "Convocatoria" else Phase.execution)
        app.create()
        app.save()
        st.success(f"✅ {title} agregado correctamente")
    
    title = st.text_input(label="Nombre del proyecto",
                          key=f"title{st.session_state.program}")
    phase = st.selectbox(label="Fase", 
                         options=["Convocatoria", "Ejecución"],
                         index=1,
                         key=f"phase{st.session_state.program}")
    code = st.text_input(label="Código", 
                         key=f"code{st.session_state.program}", disabled=phase!="Ejecución") or "No definido"
    owner = st.text_input(label="Correo del Jefe de Proyecto",
                          key=f"owner{st.session_state.program}")
    institution = st.text_input(label="Institución",
                                key=f"institution{st.session_state.program}")
    project_type = st.selectbox(label="Tipo de proyecto", 
                                options=list(program[phase]["project_types"].keys()), 
                                disabled=not phase, 
                                key=f"project-type{st.session_state.program}")

    button = st.button(label="Agregar", 
                       on_click=add_project, 
                       args=(title, owner, phase, project_type, institution, code), 
                       disabled=not (title and owner and phase and project_type and institution and code),
                       key=f"add-project{st.session_state.program}")

def update_database() -> None:
    "Actualizar campos de la Base de Datos"
    if st.session_state.user == "mvilasvaliente@gmail.com" or st.session_state.user == "develop":
        st.button(label="Actualizar BD", on_click=checker.check_apps, kwargs={"program":st.session_state.program.lower()})
    else:
        st.error(icon="🚨", body="Usted no tiene acceso a esta función")

with sections[1]:
    st.write(f"#### Evaluación de los expertos")
    anexo = config["programs"][app.program][app.phase.value]["project_types"][app.project_type]["doc"]
    name = config["docs"][anexo]["name"]
    file_name_u = config["docs"][anexo]["upload"]["file_name"]
    extension_u = config["docs"][anexo]["upload"]["extension"]
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
        
            exp_file = app.file(file_name=file_name_u, expert=exp.username)
            if exp_file:
                tab.download_button(
                    f"⏬ Descargar última versión subida del {name}", exp_file, file_name=file_name_u, key=f"down{anexo}{exp.username}{app.uuid}"
                )
            else:
                tab.warning("No hay evaluación de este experto", icon="⚠️")
                
            uploaded = tab.file_uploader(
                f"Subir {name}",
                extension_u,
                key=f"up{anexo}{exp.username}"
            )
            if uploaded:
                app.save_expert_eval(
                    expert=exp.username, 
                    file_name=anexo,
                    doc=uploaded,
                    extension=extension_u
                )
                st.success("Evaluación guardada satisfactoriamente", icon="✅")
            
            if exp.notify:
                tab.info("El experto fue notificado", icon="ℹ️")
            
            evaluation = tab.text_input(
                label="Evaluación final del experto", 
                value=exp.evaluation.final_score,
                disabled=app.phase == Phase.execution,
                key=f"evaluation_{exp.username}_dp"
            )

            if float(evaluation) != exp.evaluation.final_score:
                exp.evaluation.final_score = evaluation
                exp.evaluation.review = Status.accept
                tab.success("Evaluación guardada satisfactoriamente", icon="✅")
                app.save()
    
            email_form(tab, "program", exp.username, f"expert_{i}",
                       program=st.session_state.program, 
                       user=roles[st.session_state.program]["Dirección de Programa"][st.session_state.user]
            )
                    
            tab.button(label="⛔ Quitar asignación", on_click=unassign_expert, args=[app, evaluators[i]], key=f"u_expert{i}_{app.uuid}")
    
manage = {func.__doc__: func for func in [add_user, del_user, add_project, update_database]}    

with sections[2]:
    st.info("Recuerde presionar Enter para que se guarden los campos correctamente", icon="ℹ️")
    option = st.selectbox("Seleccione una opción", list(manage.keys()), key="manage")
    st.write(f"#### {option}")
    manage[option]()
