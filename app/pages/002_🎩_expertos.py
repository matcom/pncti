import streamlit as st
import auth

st.set_page_config(page_title="PNCTI (Demo) - Expertos", page_icon="🎩", layout="wide")

st.header('🎩 Expertos')

user = auth.authenticate()

if st.session_state.role != "Experto":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Experto**.")
    st.stop()

st.info("Usted tiene asignados **3** aplicaciones a revisar.")

app = st.selectbox("Seleccione la aplicación", ["Aplicación %i" %i for i in range(1,4)])

st.write(f"### {app}")

st.write("**Título:**")
st.write("**Jefe de Proyecto:**")
st.write("**Entidad Ejecutora Principal:**")

st.download_button(
    label="⬇️ Descargar Anexo 3", 
    data="Nada que ver aquí", 
    file_name="Anexo-3.docx"
    )

st.download_button(
    label="⬇️ Descargar Aval del CC", 
    data="Nada que ver aquí", 
    file_name="AvalCC.pdf"
    )

st.write("#### Evaluación")

total = 0

cols = st.columns([2,1])
cols[0].write("Descripción del indicador 1")
total += cols[1].slider("Indicador 1", 1,10)

cols = st.columns([2,1])
cols[0].write("Descripción del indicador 2")
total += cols[1].slider("Indicador 2", 1,10)

cols = st.columns([2,1])
cols[0].write("Descripción del indicador 3")
total += cols[1].slider("Indicador 3", 1,10)

cols = st.columns([2,1])
cols[0].write("Descripción del indicador 4")
total += cols[1].slider("Indicador 4", 1,10)

cols = st.columns([2,1])
cols[0].write("Descripción del indicador 5")
total += cols[1].slider("Indicador 5", 1,10)

st.write(f"**Evaluación total:** {total} puntos")

if st.file_uploader("Subir evaluación cualitativa"):
    st.info("ℹ️ Si está seguro de la evaluación, haga click en el siguiente botón.")
    st.button("🟢 Completar evaluación")