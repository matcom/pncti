import streamlit as st
import random
import auth

st.set_page_config("PNCTI (Demo) - Aplicaciones", page_icon="📑", layout="wide")

st.header('📑 Aplicaciones')

user = auth.authenticate()

st.info("En el sistema hay **14** aplicaciones")

app = st.selectbox("Seleccione una aplicación", ["Aplicación %i" % i for i in range(1,15)])
rnd = random.Random(app)

st.write(f"### {app}")

st.write(f"#### Documentación de la aplicación")

st.download_button("🔽 Descargar Anexo 3", "Nada que ver aqui", "Doc.txt")
st.download_button("🔽 Descargar Aval del CC", "Nada que ver aqui", "Doc.txt")
st.download_button("🔽 Descargar Presupuesto", "Nada que ver aqui", "Doc.txt")

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