import streamlit as st
from models import Application, Status
from yaml import safe_load

config = safe_load(open("/src/data/config.yml"))


def replace_file(app, file_name, buffer):
    with app.file(file_name, "wb") as fp:
        fp.write(buffer)
        st.success("Archivo modificado con éxito")


def update_app(app, title, type):
    app.title = title
    app.project_type = type
    app.save()
    st.success(f"Aplicación **{app.title}** modificada con éxito.")

def show_app_state(app, expert=False):
    st.write(f"### {app.title} - {app.project_type}")
    if app.moved:
        st.info(f"Esta aplicación viene del programa {app.moved}", icon="ℹ️")
    left, right = st.columns(2)

    with right:
        st.write(f"#### Documentación de la aplicación")
        st.download_button("📦 Descargar toda", app.zip_file(), file_name=f"{app.title}.zip")
        for key in config["programs"][app.program]["docs"].keys():
            name = config["docs"][key]["name"]
            file_name = config["docs"][key]["file_name"]
            
            exist =  app.file(file_name)
            if not expert:
                uploaded = st.file_uploader(
                    f"Reemplazar {name}" if exist else f"Subir {name}",
                    config["docs"][key]["extension"],
                    key=key,
                )

                if uploaded:
                    st.button("💾 Reemplazar", on_click=replace_file, args=(app, file_name, uploaded.getbuffer()), key=f"{key}_replace")
            
            if exist:
                st.download_button(
                    f"📄 Descargar {name}", app.file(file_name).read(), file_name
                )
            else:
                st.warning(f"No se ha subido el {name}", icon="⚠️")
        

    with left:
        if not expert:
            st.write("#### Modificar metadatos")

            program = config['programs'][st.session_state.program]

            new_title = st.text_input("Nuevo título", value=app.title)
            new_type = st.selectbox("Tipo de proyecto", program['project_types'], index=list(program['project_types']).index(app.project_type))

            st.button("💾 Modificar", on_click=update_app, args=(app, new_title, new_type))

            st.write("#### Estado de la aplicación")

        def report_status(title, value):
            if value == Status.pending:
                st.warning(f"🟡 {title}: **Pendiente**")
            elif value == Status.reject:
                st.error(f"🔴 {title}: **Rechazado**")
            elif value == Status.accept:
                st.success(f"🟢 {title}: **Completado**")

        report_status("Revisión de la documentación inicial", app.doc_review)
        for key,value in app.experts.items():
            report_status(f"Evaluación del {key}", value.evaluation.review)
        report_status("Evaluación Final", app.overal_review)

    return left, right
