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

applications = list(Application.load_from(program=st.session_state.program, user=st.session_state.user, expert=True))

st.info(f"Usted tiene **{len(applications)}** aplicaciones asignadas.")

app: Application = st.selectbox("Seleccione una aplicación", applications, format_func=lambda app: app.title)

if not app:
    st.stop()

show_app_state(app, expert=True)

left, right = st.columns(2)
with left:
    score = st.number_input(label="Inserte la puntuación", min_value=0, value=0)
    if score:
        if app.expert_1 == st.session_state.user:
            app.expert_1_score = score
        else:
            app.expert_2_score = score
        app.save()
        st.success("✅ Se ha introducido la puntuación correctamente")
    else: 
        st.warning("⚠️ Debe introducir la puntuación")
    
with right:
    pt = config["programs"][app.program]["project_types"][app.project_type]
    name = config["docs"][pt]["name"]
    file_name = config["docs"][pt]["file_name"]
    
    
    uploaded = st.file_uploader(
        f"Subir {name}",
        config["docs"][pt]["extension"],
        key=pt
    )
    st.download_button(
        f"⏬ Descargar {name}", open(f"{st.session_state.path}/docs/{file_name}", "rb").read(), file_name=file_name
    )

    if uploaded:
        # Guardar archivo
        pass
        

