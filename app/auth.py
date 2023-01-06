import streamlit as st
from tools import send_from_template
import extra_streamlit_components as stx
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import BadData
import yaml
import os

info = yaml.safe_load(open("/src/app/info.yml"))['auth']
cookie = "PNCTI-AuthToken"


def login(user):
    st.session_state.user = user
    st.experimental_set_query_params()
    st.sidebar.info(f"Bienvenido **{user}**")
    set_token_in_cookies(generate_signin_token(user))
    st.sidebar.button("🚪 Cerrar sesión", on_click=logout)

    return user


def logout():
    del st.session_state['user']
    delete_token_in_cookies()


def authenticate():
    token = st.experimental_get_query_params().get('token')

    if token:
        user = verify_token(token[0])

        if user is not None:
            return login(user)
        else:
            st.error("El token de autenticación es inválido. Vuelva a intentarlo.")
    elif "user" in st.session_state:
        user = st.session_state.user
        return login(user)
    else:
        token = get_token_from_cookies()
        user = verify_token(token)

        if user is not None:
            return login(user)

    st.warning("⚠️ Antes de continuar, debe registrarse en la plataforma.")

    left, right = st.columns(2)

    with left:
        role = st.selectbox("Seleccione el rol que desea acceder", ["Gestor de Proyecto", "Experto", "Gestor de Programa"])
        email = st.text_input("Introduza su dirección correo electrónico")
    with right:
        st.info(info[role])

    if email:
        st.info(f"""
            Haga click en el botón siguiente y le enviaremos a **{email}** un enlace de autenticación que
            le permitirá acceder a la plataforma con el rol de **{role}**.
        """)

        if st.button("📧 Enviar enlace de autenticación"):
            token = generate_signin_token(email)
            send_from_template("login", email, role=role, link=f"http://localhost:8501?token={token}")
            st.success("El enlace de autenticación ha sido enviado. Verifique su correo.")

    st.stop()


def generate_signin_token(username):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET"))
    return serializer.dumps(username)


def verify_token(token):
    if not token:
        return None

    serializer = URLSafeTimedSerializer(os.getenv("SECRET"))

    try:
        return serializer.loads(token, max_age=3600)
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
