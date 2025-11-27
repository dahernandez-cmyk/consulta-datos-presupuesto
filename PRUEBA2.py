import streamlit as st
# Aunque no lo usemos, lo dejamos para evitar errores si lo tienes en requirements.txt
import pandas as pd 

# --- 0. CONFIGURACIÓN INICIAL DEL ESTADO DE SESIÓN ---
# Inicializa las variables de sesión al inicio del script
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

# --- 1. DEFINICIÓN DE USUARIOS Y CONTRASEÑAS ---
USUARIOS = {
    "jose.d": "pass123",     
    "companero1": "seguro456",
    "admin": "admin2026"
}

# -------------------------------------------------------------------------
# FUNCIÓN DE INICIO DE SESIÓN (LOGIN PAGE)
# -------------------------------------------------------------------------

def login_form():
    """Muestra el formulario de inicio de sesión."""
    st.title("🔐 Iniciar Sesión")
    st.subheader("Acceso a Consulta de Valores")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Ingresar")

    if submit_button:
        # Verifica las credenciales
        if username in USUARIOS and USUARIOS[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.rerun() # Recarga la página
        else:
            st.error("Usuario o contraseña incorrectos.")

# -------------------------------------------------------------------------
# FUNCIÓN DE CONTENIDO PRINCIPAL MÍNIMO (Para probar el flujo)
# -------------------------------------------------------------------------

def main_app():
    """Contenido simple que se muestra después de un login exitoso."""
    st.title('¡Login Exitoso! ✅')
    st.success(f"Bienvenido, {st.session_state['username']}. La lógica de navegación funciona.")
    st.warning("Ahora debemos reinsertar la carga del CSV.")
    
    # Botón de Cerrar Sesión
    if st.button("🔓 Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.rerun()

# -------------------------------------------------------------------------
# LÓGICA DE NAVEGACIÓN PRINCIPAL
# -------------------------------------------------------------------------

if st.session_state['logged_in']:
    main_app()
else:
    login_form()