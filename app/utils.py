import streamlit as st
from models import Application, Status, Phase
from yaml import safe_load
import datetime

config = safe_load(open("/src/data/config.yml"))

def replace_file(app, file_name, buffer):
    with app.file(file_name, "wb") as fp:
        fp.write(buffer)
        st.success("Archivo modificado con éxito")


def update_app(app, title, type, institution, owner, code):
    app.title = title
    app.project_type = type
    app.institution = institution
    app.owner = owner
    app.code = code
    app.save()
    st.success(f"Aplicación **{app.title}** modificada con éxito.")

def show_docs(app: Application, docs: list, replaceable: bool = True):
    for key in (docs):
        name = config["docs"][key]["name"]
        file_name_u = config["docs"][key]["upload"]["file_name"]
        extension_u = config["docs"][key]["upload"]["extension"]
        
        exist =  app.file(file_name_u)
        if replaceable:
            uploaded = st.file_uploader(
                f"Reemplazar {name}" if exist else f"Subir {name}",
                extension_u,
                key=key,
            )

            if uploaded:
                st.button("💾 Reemplazar" if exist else "💾 Subir", on_click=replace_file, args=(app, file_name_u, uploaded.getbuffer()), key=f"{key}_replace")
        
        if exist:
            st.download_button(
                f"📄 Descargar {name}", app.file(file_name_u).read(), file_name_u
            )
        else:
            st.warning(f"No se ha subido el {name}", icon="⚠️")

def show_app_state(app, expert=False):
    st.write(f"### {app.title} - {app.project_type}")
    if app.moved:
        st.info(f"Esta aplicación viene del programa {app.moved}", icon="ℹ️")
    left, right = st.columns(2)
    with right:
        st.write(f"#### Documentación de la aplicación")
        st.download_button("📦 Descargarla toda", app.zip_file(), file_name=f"{app.title}.zip", help="Descarga un comprimido con todos los archivos del proyecto")
        # App docs
        show_docs(app=app, 
                  docs=config["programs"][app.program][app.phase.value]["docs"].keys(), 
                  replaceable=not expert)
        # Expert docs
        if (app.phase.value == "Ejecución" and 
            (st.session_state.role == "Dirección de Proyecto" or st.session_state.role == "Dirección de Programa")):
            st.write("**Documentos de los Expertos**")
            anexo = config["programs"][app.program][app.phase.value]["project_types"][app.project_type]["doc"]
            name = config["docs"][anexo]["name"]
            file_name_u = config["docs"][anexo]["upload"]["file_name"]
            for exp in app.experts.values():
                if not exp.username:
                    st.warning("No está asignado", icon="⚠️")   
                else:
                    st.write(f"Evaluación del experto {exp.username}")
                    exp_file = app.file(file_name=file_name_u, expert=exp.username)
                    if exp_file:
                        st.download_button(
                            f"⏬ Descargar última versión subida del {name}", exp_file, file_name=file_name_u)
                    else:
                        st.warning("No hay evaluación de este experto", icon="⚠️")

        # Admin docs
        if (app.phase.value == "Ejecución"):
            st.write("**Documentos de la Dirección del Programa**")
            show_docs(app=app, 
                    docs=config["programs"][app.program][app.phase.value]["dir_program"]["docs"],
                    replaceable=st.session_state.role == "Dirección de Programa")
    with left:
        if not expert:
            st.write("#### Modificar metadatos")
            st.info("Recuerde presionar Enter para que se guarden los campos correctamente", icon="ℹ️")
            program = config['programs'][st.session_state.program]

            new_title = st.text_input("Nuevo título", value=app.title)
            new_type = st.selectbox("Tipo de proyecto", program[app.phase.value]['project_types'], index=list(program[app.phase.value]['project_types']).index(app.project_type))
            new_institution = st.text_input("Nueva Institución", value=app.institution)
            new_owner = st.text_input("Correo del Jefe de Proyecto", value=app.owner, disabled=st.session_state.role != "Dirección de Programa")
            new_code = st.text_input("Código del proyecto", value=app.code, disabled=app.phase.value != Phase.execution.value or st.session_state.role != "Dirección de Programa")
            st.button("💾 Modificar", on_click=update_app, args=(app, new_title, new_type, new_institution, new_owner, new_code))

        def report_status(title, value: Status):
            if value == Status.pending or value == Status.aproved:
                st.warning(f"🟡 {title}: **{value.value}**")
            elif value == Status.reject or value == Status.not_aproved:
                st.error(f"🔴 {title}: **{value.value}**")
            elif value == Status.accept or value == Status.selected:
                st.success(f"🟢 {title}: **{value.value}**")
        if app.phase == Phase.announcement:  
            st.write("#### Estado de la aplicación")
            report_status("Revisión de la documentación inicial", app.doc_review)
            for key,value in app.experts.items():
                report_status(f"Evaluación del {key}", value.evaluation.review)
            report_status("Evaluación Final", app.overal_review)

    return left, right
