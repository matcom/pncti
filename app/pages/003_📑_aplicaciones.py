import streamlit as st
import random
import auth

st.set_page_config("PNCTI (Demo) - Aplicaciones", page_icon="📑", layout="wide")

st.header('📑 Aplicaciones')

user = auth.authenticate()

if st.session_state.role != "Dirección de Programa":
    st.warning("⚠️ Esta sección solo está disponible para el rol de **Dirección de Programa**.")
    st.stop()

st.info("En el sistema hay **14** aplicaciones")

app = st.selectbox("Seleccione una aplicación", ["Aplicación %i" % i for i in range(1,15)])
rnd = random.Random(app)

st.write(f"### {app}")

st.write(f"#### Documentación de la aplicación")

st.download_button(
    label="🔽 Descargar Anexo 3", 
    data="Nada que ver aqui", 
    file_name="Anexo-3.docx"
    )

st.download_button(
    label="🔽 Descargar Aval del CC", 
    data="Nada que ver aqui", 
    file_name="AvalCC.pdf"
    )

st.download_button(
    label="🔽 Descargar Presupuesto", 
    data="Nada que ver aqui", 
    file_name="Presupuesto.xlsx"
    )

st.write("#### Revisión (paso 1)")

st.write("##### Anexo 3")

st.warning("ℹ️ No se ha revisado el Anexo 3")
st.button("👍 Aprobar Anexo 3")
st.button("👎 Rechazar Anexo 3")

st.write("##### Aval del CC")

st.success("✅ Se aprobó el Aval del CC")

st.write("##### Presupuesto")

st.success("✅ Se aprobó el Presupuesto")

st.write("### Expertos")

st.selectbox("Asignar a experto:", ["Experto %i" % i for i in range(1,21)])
st.button("👍 Asignar")