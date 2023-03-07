import streamlit as st
import yaml
import auth
from tools import check_file

from models import Application

st.set_page_config(page_title="PNCTI (Demo)", page_icon="⭐", layout="wide")
user = auth.authenticate()

info = yaml.safe_load(open("/src/data/info.yml"))
config = yaml.safe_load(open("/src/data/config.yml"))

announcement = config['programs'][st.session_state.program]['announcement']
st.header(
    announcement['header']
)

st.write(
    announcement['top_msg']
)

if st.session_state.role != "Dirección de Proyecto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Dirección de Proyecto**.")
    st.stop()


def send_application(title, project_type, *args):
    app = Application(title=title, project_type=project_type, program=st.session_state.program, owner=st.session_state.user, path=st.session_state.path)
    app.create(docs=args)

    st.session_state.title = ""
    st.session_state.project_type = ""
    del st.session_state.anexo3
    del st.session_state.avalCC
    del st.session_state.presupuesto

    st.success("**🥳 ¡Su aplicación ha sido guardada con éxito!**")


st.info(
    info['msgs']['new_msg']
)

st.write("### Datos del Proyecto")

program = config['programs'][st.session_state.program]

left, right = st.columns(2)

with right:
    msg = announcement["basic"]
    for pt in program['project_types']:
        msg += f"- **{pt}**: {info['project_types'][pt]}\n"
    st.info(msg)

with left:
    title = st.text_input("Título del proyecto", key="title")
    project_type = st.selectbox("Tipo de proyecto", [""] + program['project_types'], key="project_type")

    if len(title.split()) > 5 and project_type:
        st.success("✅ Título y tipo de proyecto definido correctamente.")
    else:
        st.warning("⚠️ Debe definir un título (no menor de 5 palabras) y el tipo del proyecto antes de continuar con la aplicación")
        st.stop()


ready = True

args = [title, project_type]

for key, value in program['docs'].items():
    name = config['docs'][key]['name']
    extension = config['docs'][key]['extension']
    file_name = config['docs'][key]['file_name']

    st.write(f"### {name}")
    left, right = st.columns(2)

    with left:
        if value["upload"]:
            fd = st.file_uploader(f"Subir {name}", extension, key=key)

        if value["download"]:
            st.download_button(
                "⏬ Descargar Modelo", open(f"{st.session_state.path}/docs/{file_name}", "rb").read(), file_name=file_name
            )

        if fd: #check_file...
            st.success(f"✅ {name} verificado.")
            args.append({"key": key, "file": fd, "extension": extension})
        else:
            st.error(f"⚠️ Falta {name}")
            ready = False

    with right:
        st.info(f"ℹ️ **Sobre el {name}**\n\n" + info['docs'][key])
        # st.info(f"ℹ️ **Sobre el {name}**\n\n{info[key]}\n\n_{title}_ - _{project_type}_")

st.write("---")

if ready:
    st.success("✅ " + info['msgs']['success'])
    st.button("⬆️ Enviar aplicación", on_click=send_application, args=args)
else:
    st.warning("⚠️ " + info['msgs']['missing'])
