import streamlit as st
from tools import send_from_template
import extra_streamlit_components as stx
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import BadData
import yaml
import os

info = yaml.safe_load(open("/src/data/info.yml"))['auth']
roles = yaml.safe_load(open("/src/data/roles.yml"))
config = yaml.safe_load(open("/src/data/config.yml"))
cookie = "PNCTI-AuthToken"


def login(user, role, program):
    st.session_state.user = user
    st.session_state.role = role
    st.session_state.program = program
    st.session_state.path = config["programs"][program]["path"]
    st.experimental_set_query_params()
    st.sidebar.info(f"Bienvenido **{user}**\n\nRol: **{role}**\n\nPrograma: **{program}**")
    set_token_in_cookies(generate_signin_token(user, role, program))
    st.sidebar.button("🚪 Cerrar sesión", on_click=logout)

    if user == os.getenv("ADMIN"):
        new_program = st.sidebar.selectbox("Cambiar programa",
                                           [prog[1]["name"] for prog in config["programs"].items()])
        new_program = program.split('-')[0].strip()
        new_role = st.sidebar.selectbox("Cambiar rol", config["roles"])
        st.sidebar.button("🪄 Cambiar", on_click=login, args=(user, new_role, new_program))

    return user


def logout():
    del st.session_state['user']
    delete_token_in_cookies()


def authenticate():
    if os.getenv('IGNORE_AUTH'):
        user = os.getenv("ADMIN")
        role = st.session_state.get('role', config['roles'][2])
        program = st.session_state.get('program', list(config['programs'].items())[1][0])
        return login(user, role, program)

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
        path = st.session_state.path
        return login(user, role, program)
    else:
        token = get_token_from_cookies()
        credentials = verify_token(token)

        if credentials is not None:
            return login(*credentials)

    st.warning("⚠️ Antes de continuar, debe autenticarse en la plataforma.")

    left, right = st.columns(2)

    with left:
        role = st.selectbox("Seleccione el rol que desea acceder", config["roles"])
        program = st.selectbox("Seleccione el Programa", [prog[1]["name"] for prog in config["programs"].items()])
        program = program.split('-')[0].strip()
        email = st.text_input("Introduza su dirección correo electrónico").strip()
    with right:
        st.info("ℹ️ " + info[role])

    if email:
        if not check_email_role(email, program, role):
            st.error(f"El correo electrónico **{email}** no tiene permitido el rol **{role}** en el programa **{program}**.")
            st.stop()

        st.info(f"""
            Haga click en el botón siguiente y le enviaremos a **{email}** un enlace de autenticación que
            le permitirá acceder a la plataforma con el rol de **{role}** en el programa **{program}**.
        """)

        if st.button("📧 Enviar enlace de autenticación"):
            token = generate_signin_token(email, role, program)
            host = os.getenv("HOSTNAME")
            try:
                send_from_template("login", email, role=role, program=program, link=f"{host}?token={token}")
                st.success("El enlace de autenticación ha sido enviado. Verifique su correo.")
            except Exception as e:
                st.error("**ERROR**: " + str(e))

                with st.expander("Ver detalles del error"):
                    st.exception(e)

    st.stop()


def check_email_role(email, program, role):
    if role == "Dirección de Proyecto":
        return True

    if email == os.getenv("ADMIN"):
        return True

    return email in roles[program][role]


def generate_signin_token(user, role, program):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET"))
    return serializer.dumps(f"{user}::{role}::{program}")


def verify_token(token):
    if not token:
        return None

    serializer = URLSafeTimedSerializer(os.getenv("SECRET"))

    try:
        return serializer.loads(token, max_age=7 * 24 * +3600).split("::")
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
