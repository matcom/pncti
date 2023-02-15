import streamlit as st
from models import Application, Status


def show_app_state(app):
    st.write(f"### {app.title} - {app.project_type}")

    left, right = st.columns(2)

    with right:
        st.write(f"#### Documentación de la aplicación")

        st.download_button("📄 Descargar Anexo 3", app.file("Anexo3.docx").read(), "Anexo3.docx")
        st.download_button("📄 Descargar Aval del CC", app.file("AvalCC.pdf").read(), "AvalCC.pdf")
        st.download_button("📄 Descargar Presupuesto", app.file("Presupuesto.xlsx").read(), "Presupuesto.xlsx")

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
