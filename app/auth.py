import streamlit as st
from tools import send_from_template
import extra_streamlit_components as stx
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import BadData
import yaml
import os

info = yaml.safe_load(open("/src/app/info.yml"))['auth']
cookie = "PNCTI-AuthToken"


def login(user, role, program):
    st.session_state.user = user
    st.session_state.role = role
    st.session_state.program = program
    st.experimental_set_query_params()
    st.sidebar.info(f"Bienvenido **{user}**\n\nRol: **{role}**\n\nPrograma: **{program}**")
    set_token_in_cookies(generate_signin_token(user, role, program))
    st.sidebar.button("🚪 Cerrar sesión", on_click=logout)

    return user


def logout():
    del st.session_state['user']
    delete_token_in_cookies()


def authenticate():
    token = st.experimental_get_query_params().get('token')

    if token:
        credentials = verify_token(token[0])

        if credentials is not None:
            return login(*credentials)
        else:
            st.error("El token de autenticación es inválido. Vuelva a intentarlo.")
    elif "user" in st.session_state:
        user = st.session_state.user
        role = st.session_state.role
        program = st.session_state.program
        return login(user, role, program)
    else:
        token = get_token_from_cookies()
        credentials = verify_token(token)

        if credentials is not None:
            return login(*credentials)

    st.warning("⚠️ Antes de continuar, debe registrarse en la plataforma.")

    left, right = st.columns(2)

    with left:
        role = st.selectbox("Seleccione el rol que desea acceder", ["Jefe de Proyecto", "Experto", "Gestor de Programa"])
        program = st.selectbox("Seleccione el Programa", ["PNCB - Ciencias Básicas", "HCS - Humanidades y Ciencias Sociales", "TIS - Telecomunicaciones e Informatización de la Sociedad"])
        email = st.text_input("Introduza su dirección correo electrónico")
    with right:
        st.info(info[role])

    if email:
        st.info(f"""
            Haga click en el botón siguiente y le enviaremos a **{email}** un enlace de autenticación que
            le permitirá acceder a la plataforma con el rol de **{role}** en el programa **{program}**.
        """)

        if st.button("📧 Enviar enlace de autenticación"):
            token = generate_signin_token(email, role, program)
            try:
                send_from_template("login", email, role=role, program=program, link=f"http://localhost:8501?token={token}")
                st.success("El enlace de autenticación ha sido enviado. Verifique su correo.")
            except Exception as e:
                st.error("**ERROR**: " + str(e))

                with st.expander("Ver detalles del error"):
                    st.exception(e)

    st.stop()


def generate_signin_token(user, role, program):
    program = program.split("-")[0].strip()
    serializer = URLSafeTimedSerializer(os.getenv("SECRET"))
    return serializer.dumps(f"{user}::{role}::{program}")


def verify_token(token):
    if not token:
        return None

    serializer = URLSafeTimedSerializer(os.getenv("SECRET"))

    try:
        return serializer.loads(token, max_age=3600).split("::")
    except BadData:
        return None


def _get_cookie_manager():
    if "cookie_manager" in st.session_state:
        return st.session_state.cookie_manager

    cookie_manager = stx.CookieManager()
    st.session_state.cookie_manager = cookie_manager
    return cookie_manager


def get_token_from_cookies():
    cookie_manager = _get_cookie_manager()
    cookie_manager.get_all()
    auth_token = cookie_manager.get(cookie)
    return auth_token


def set_token_in_cookies(token):
    cookie_manager = _get_cookie_manager()
    cookie_manager.set(cookie, token, expires_at=None)


def delete_token_in_cookies():
    cookie_manager = _get_cookie_manager()
    cookie_manager.delete(cookie)
