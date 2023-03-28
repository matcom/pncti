import streamlit as st
import auth
import yaml
from models import Application, Status
from utils import show_app_state

st.set_page_config(page_title="Proyectos UH - Expertos", page_icon="🎩", layout="wide")
user = auth.authenticate()

st.header('🎩 Expertos')

config = yaml.safe_load(open("/src/data/config.yml"))

if st.session_state.role != "Experto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Experto**.")
    st.stop()

applications = Application.load_from(program=st.session_state.program, user=st.session_state.user, expert=True)


st.info(f"Usted tiene **{len(applications)}** aplicaciones asignadas.")

app: Application = applications[st.selectbox("Seleccione una aplicación", applications)]

if not app:
    st.stop()

left, right = show_app_state(app, expert=True)

with right:
    st.write("#### Evaluación")

    anexo = config["programs"][app.program]["project_types"][app.project_type]["doc"]
    name = config["docs"][anexo]["name"]
    file_name = config["docs"][anexo]["file_name"]
    extension = config["docs"][anexo]["extension"]

    uploaded = st.file_uploader(
        f"Subir {name}",
        extension,
        key=anexo
    )

    last_version = app.file(file_name, expert=st.session_state.user)
    if last_version:
        st.download_button(
        f"⏬ Descargar última versión", last_version.read(), file_name=file_name
    )
    else:
        st.download_button(
        f"⏬ Descargar plantilla del {name}", open(f"{st.session_state.path}/docs/{file_name}", "rb").read(), file_name=file_name
    )
          
    if uploaded:
        app.save_expert_eval(expert=st.session_state.user, 
                             file_name=anexo,
                             doc=uploaded,
                             extension=extension)
        st.success("Evaluación guardada satisfactoriamente", icon="✅")
        
    value = st.number_input(label="Evaluación Final", 
                            max_value=config["programs"][st.session_state.program]["project_types"][app.project_type]["max_value"], 
                            min_value=0, 
                            step=5)
    for role, expert in app.experts.items():
        if st.session_state.user == expert.username:
            expert.evaluation.review = Status.accept
            expert.evaluation.final_score = value
            app.save()
            break