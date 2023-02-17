import streamlit as st
from models import Application, Status
from yaml import safe_load

config = safe_load(open("/src/data/config.yml"))

def show_app_state(app):
    st.write(f"### {app.title} - {app.project_type}")

    left, right = st.columns(2)

    with right:
        st.write(f"#### Documentación de la aplicación")
        for key in config['programs'][app.program]['docs'].keys():
            name = config['docs'][key]['name']
            file_name = config['docs'][key]['file_name']
            
            st.download_button(f"📄 Descargar {name}", app.file(file_name).read(), file_name)

    with left:
        st.write("#### Estado de la aplicación")

        def report_status(title, value):
            if value == Status.pending:
                st.warning(f"🟡 {title}: **Pendiente**")
            elif value == Status.reject:
                st.error(f"🔴 {title}: **Rechazado**")
            elif value == Status.accept:
                st.success(f"🟢 {title}: **Completado**")

        report_status("Revisión de la documentación inicial", app.doc_review)
        report_status("Evaluación del Experto No. 1", app.expert_1_review)
        report_status("Evaluación del Experto No. 2", app.expert_2_review)
        report_status("Evaluación del Presupuesto", app.budget_review)
        report_status("Evaluación del Impacto Social", app.social_review)
        report_status("Evaluación Final", app.overal_review)

    return left, right
