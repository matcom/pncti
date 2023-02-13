import streamlit as st
import yaml
import auth

from models import Application


st.set_page_config(page_title="PNCTI (Demo)", page_icon="⭐", layout="wide")
info = yaml.safe_load(open("/src/data/info.yml"))['convocatoria']

st.header(
    info['header']
)

st.write(
    info['top_msg']
)

user = auth.authenticate()

if st.session_state.role != "Dirección de Proyecto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Dirección de Proyecto**.")
    st.stop()


def send_application(title, project_type, anexo3, avalCC, presupuesto):
    app = Application(title=title, project_type=project_type, program=st.session_state.program, owner=st.session_state.user)
    app.create(anexo3=anexo3, avalCC=avalCC, presupuesto=presupuesto)

    st.session_state.title = ""
    st.session_state.project_type = ""
    del st.session_state.anexo3
    del st.session_state.avalCC
    del st.session_state.presupuesto

    st.success("**🥳 ¡Su aplicación ha sido guardada con éxito!**")


st.info(
    info['new_msg']
)

st.write("### Datos del Proyecto")

left, right = st.columns(2)

with right:
    st.info(info["basico"])

with left:
    title = st.text_input("Título del proyecto", key="title")
    project_type = st.selectbox("Tipo de proyecto", ["", "Investigación Básica", "Investigación Aplicada y Desarrollo", "Innovación"], key="project_type")

    if len(title.split()) > 5 and project_type:
        st.success("✅ Título y tipo de proyecto definido correctamente.")
    else:
        st.warning("⚠️ Debe definir un título (no menor de 5 palabras) y el tipo del proyecto antes de continuar con la aplicación")
        st.stop()


ready = True

st.write("### Anexo 3")

left, right = st.columns(2)

with left:
    anexo3 = st.file_uploader("Subir Anexo 3", ["docx"], key="anexo3")

    st.download_button(
        "⏬ Descargar Modelo", open("/src/data/docs/Anexo-3.docx", "rb").read(), file_name="Anexo-3.docx"
    )

    if anexo3:
        st.success("✅ Anexo 3 verificado.")
    else:
        st.error("⚠️ Falta Anexo 3")
        ready = False

with right:
    st.info(f"ℹ️ **Sobre el Anexo 3**\n\n{info['anexo_3']}\n\n_{title}_ - _{project_type}_")


st.write("### Aval del Consejo Científico")

left, right = st.columns(2)

with left:
    avalCC = st.file_uploader("Subir Aval del CC", ["docx"], key="avalCC")

    if avalCC:
        st.success("✅ Aval del CC verificado.")
    else:
        st.error("⚠️ Falta Aval del CC")
        ready = False

with right:
    st.info("ℹ️ **Sobre el Aval del CC**\n\n" + info['aval_cc'])


st.write("### Presupuesto")

left, right = st.columns(2)

with left:
    presupuesto = st.file_uploader("Subir Presupuesto", ["xlsx"], key="presupuesto")

    st.download_button(
        "⏬ Descargar Modelo", open("/src/data/docs/Presupuesto.xlsx", "rb").read(), file_name="Presupuesto.xlsx"
    )

    if presupuesto:
        st.success("✅ Presupuesto verificado.")
    else:
        st.error("⚠️ Falta Presupuesto")
        ready = False

with right:
    st.info("ℹ️ **Sobre el Presupuesto**\n\n" + info['presupuesto'])

st.write("---")

if ready:
    st.success("✅ " + info['success'])
    st.button("⬆️ Enviar aplicación", on_click=send_application, args=(title, project_type, anexo3, avalCC, presupuesto))
else:
    st.warning("⚠️ " + info['missing'])
