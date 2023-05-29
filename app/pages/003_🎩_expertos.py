import streamlit as st
import auth
import yaml
from models import Application, Status, Phase
from utils import show_app_state

st.set_page_config(page_title="Proyectos UH - Expertos", page_icon="🎩", layout="wide")
user = auth.authenticate()

st.header('🎩 Expertos')

config = yaml.safe_load(open("/src/data/config.yml"))

if st.session_state.role != "Experto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Experto**.")
    st.stop()

applications = Application.load_from(program=st.session_state.program, user=st.session_state.user, expert=True)

phases = [Phase.announcement, Phase.execution]
phase = st.select_slider("Mostrar proyectos en:", map(lambda x: x.value, phases), value=Phase.execution.value)
applications = Application.load_from(program=st.session_state.program, user=st.session_state.user, phase=phase)

st.info(f"Usted tiene **{len(applications)}** proyectos asignados.")

app: Application = applications[st.selectbox("Seleccione un proyecto", applications)]

if not app:
    st.stop()

app.save()

left, right = show_app_state(app, expert=True)

with right:
    st.write("#### Evaluación")

    anexo = config["programs"][app.program][phase]["project_types"][app.project_type]["doc"]
    name = config["docs"][anexo]["name"]
    file_name_d = config["docs"][anexo]["download"]["file_name"]
    file_name_u = config["docs"][anexo]["upload"]["file_name"]
    extension_u = config["docs"][anexo]["upload"]["extension"]

    uploaded = st.file_uploader(
        f"Subir {name}",
        extension_u,
        key=anexo
    )

    last_version = app.file(file_name_u, expert=st.session_state.user)
    if last_version:
        st.download_button(
        f"⏬ Descargar última versión", last_version.read(), file_name=file_name_u
    )
    else:
        st.download_button(
        f"⏬ Descargar plantilla del {name}", open(f"{st.session_state.path}/docs/{file_name_d}", "rb").read(), file_name=file_name_d
    )
          
    if uploaded:
        app.save_expert_eval(expert=st.session_state.user, 
                             file_name=anexo,
                             doc=uploaded,
                             extension=extension_u)
        st.success("Evaluación guardada satisfactoriamente", icon="✅")
        
    value = st.number_input(label="Evaluación Final", 
                            max_value=config["programs"][st.session_state.program][phase]["project_types"][app.project_type]["max_value"], 
                            min_value=0, 
                            step=5,
                            disabled=app.phase.value != "Convocatoria")
    for role, expert in app.experts.items():
        if st.session_state.user == expert.username:
            expert.evaluation.review = Status.accept
            expert.evaluation.final_score = value
            app.save()
            break