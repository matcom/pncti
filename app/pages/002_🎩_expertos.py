import streamlit as st
import auth

st.set_page_config(page_title="PNCTI (Demo) - Expertos", page_icon="🎩", layout="wide")

st.header('🎩 Expertos')

user = auth.authenticate()

st.info("Usted tiene asignados **3** aplicaciones a revisar.")

app = st.selectbox("Seleccione la aplicación", ["Aplicación %i" %i for i in range(1,4)])

st.write(f"### {app}")

st.write("**Título:**")
st.write("**Jefe de Proyecto:**")
st.write("**Entidad Ejecutora Principal:**")

st.download_button("⬇️ Descargar Anexo 3", "Nada que ver aquí", "Anexo3.txt")
st.download_button("⬇️ Descargar Aval del CC", "Nada que ver aquí", "AvalCC.txt")

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