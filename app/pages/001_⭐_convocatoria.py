import streamlit as st
import yaml
import auth

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

new_app, app_state = st.tabs(["🪄 Nueva aplicación", "✅ Estado de su aplicación"])

with new_app:
    st.info(
        info['new_msg']
    )

    ready = True

    st.write("### Anexo 3")

    left, right = st.columns(2)

    with left:
        fp = st.file_uploader("Subir Anexo 3")
        st.download_button(
            "⏬ Descargar Modelo", "Modelo del anexo 3", file_name="Anexo3.txt"
        )

        if fp:
            st.success("✅ Anexo 3 verificado.")
        else:
            st.error("❎ Falta Anexo 3")
            ready = False

    with right:
        st.info("ℹ️ **Sobre el Anexo 3**\n\n" + info['anexo_3'])


    st.write("### Aval del Consejo Científico")

    left, right = st.columns(2)

    with left:
        fp = st.file_uploader("Subir Aval del CC")
        st.download_button(
            "⏬ Descargar Modelo", "Modelo del Aval del CC", file_name="AvalCC.txt"
        )

        if fp:
            st.success("✅ Aval del CC verificado.")
        else:
            st.error("❎ Falta Aval del CC")
            ready = False

    with right:
        st.info("ℹ️ **Sobre el Aval del CC**\n\n" + info['aval_cc'])


    st.write("### Presupuesto")

    left, right = st.columns(2)

    with left:
        fp = st.file_uploader("Subir Presupuesto")
        st.download_button(
            "⏬ Descargar Modelo", "Modelo del Presupuesto", file_name="Presupuesto.txt"
        )

        if fp:
            st.success("✅ Presupuesto.")
        else:
            st.error("❎ Falta Presupuesto")
            ready = False

    with right:
        st.info("ℹ️ **Sobre el Presupuesto**\n\n" + info['presupuesto'])

    st.write("---")

    if ready:
        st.success("✅ " + info['success'])
        st.button("⬆️ Enviar aplicación")
    else:
        st.warning("⚠️ " + info['missing'])


with app_state:
    st.info("Usted tiene 2 aplicaciones en el sistema.")

    info = st.selectbox("Seleccione título de la aplicación", ["Aplicación 1", "Aplicación 2"])

    st.write("### Estado de la aplicación")

    if info == "Aplicación 1":
        st.success("✅ Revisado el Anexo 3")
        st.success("✅ Revisado el Aval del CC")
        st.error("❎ Error en el Presupuesto")
        st.download_button("🔽 Descargar comentarios", "Nada que ver aquí", "Informe.txt")
        if st.file_uploader("Volver a subir Presupuesto"):
            st.button("👍 Aplicar cambios")

    else:
        st.success("✅ Revisado el Anexo 3")
        st.success("✅ Revisado el Aval del CC")
        st.success("✅ Revisado el Presupuesto")
        st.success("✅ Asignado ID de Proyecto: **004**")
        st.success("✅ Informe del Experto 1")
        st.warning("⌛ Falta informe del Experto 2")
        st.warning("⌛ Falta evaluación del Presupuesto")
        st.warning("⌛ Falta evaluación del Impacto Social")
