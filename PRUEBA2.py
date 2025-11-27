import streamlit as st
import pandas as pd
# Puedes agregar la librería hashlib para contraseñas más seguras si lo deseas

# --- 0. CONFIGURACIÓN INICIAL DEL ESTADO DE SESIÓN ---
# Inicializa la variable de sesión para el login y el nombre de usuario si no existen
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

# --- 1. DEFINICIÓN DE USUARIOS Y CONTRASEÑAS ---
# ¡Asegúrate de cambiar estas credenciales por las reales!
USUARIOS = {
    "jose.d": "pass123",     # Usuario: jose.d, Contraseña: pass123
    "companero1": "seguro456",
    "admin": "admin2026"
}

# -------------------------------------------------------------------------
# FUNCIÓN DE INICIO DE SESIÓN (LOGIN PAGE)
# -------------------------------------------------------------------------

def login_form():
    """Muestra el formulario de inicio de sesión."""
    st.title("🔐 Iniciar Sesión")
    st.subheader("Consulta de Presupuesto Gasto de Personal 2026")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Ingresar")

    if submit_button:
        # Verifica las credenciales
        if username in USUARIOS and USUARIOS[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"¡Bienvenido, {username}!")
            st.rerun() # Fuerza la recarga para ir a la app principal
        else:
            st.error("Usuario o contraseña incorrectos.")

# -------------------------------------------------------------------------
# FUNCIÓN DE CONTENIDO PRINCIPAL (MAIN APP PAGE)
# -------------------------------------------------------------------------

def main_app():
    """Contenido principal de la aplicación (Filtros y Tabla)."""
    
    # ------------------- BLOQUE DE CARGA DE DATOS ----------------------
    try:
        # Intenta leer con punto y coma y latin-1
        df = pd.read_csv('prueba.csv', sep=';', encoding='latin-1')
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        st.stop() # Detiene la ejecución si hay un error de lectura
    # -------------------------------------------------------------------

    st.title('Sistema de Consulta de Presupuesto Gasto de Personal 2026')
    
    # Botón de Cerrar Sesión en la barra lateral
    st.sidebar.markdown(f"**Usuario:** {st.session_state['username']}")
    if st.sidebar.button("🔓 Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.rerun()

    # ----------------------------------------------------
    # 2. Diseño de la Interfaz y Filtros
    # ----------------------------------------------------

    # Crea el contenedor para los filtros en la barra lateral
    st.sidebar.header('Opciones de Filtro')

    # Paso A: Obtener los nombres disponibles
    nombres_disponibles = df['Nombre'].unique()

    # ----------------------------------------------------
    # 1. Checkbox para Seleccionar Todo
    # ----------------------------------------------------
    seleccionar_todo = st.sidebar.checkbox(
        "✅ Seleccionar todos los nombres", 
        value=True # Empieza marcado por defecto
    )

    # 2. Definir la lista predeterminada (default)
    if seleccionar_todo:
        lista_predeterminada = nombres_disponibles
    else:
        lista_predeterminada = []

    # ----------------------------------------------------
    # 3. Crear el Filtro Multiselect
    # ----------------------------------------------------
    nombre_seleccionado = st.sidebar.multiselect(
        'Selecciona el Nombre:',
        options=nombres_disponibles,
        default=lista_predeterminada
    )

    # ----------------------------------------------------
    # 3. Aplicar el Filtro y Mostrar el Resultado
    # ----------------------------------------------------

    # Paso B: Aplicar el filtro al DataFrame
    df_filtrado = df[df['Nombre'].isin(nombre_seleccionado)]

    # Mostrar los resultados
    st.dataframe(df_filtrado)

    # Opcional: Mostrar un resumen de cuántas filas se están viendo
    st.markdown(f"Mostrando **{len(df_filtrado)}** de **{len(df)}** registros.")


# -------------------------------------------------------------------------
# LÓGICA DE NAVEGACIÓN PRINCIPAL (Controla qué "hoja" se muestra)
# -------------------------------------------------------------------------

if st.session_state['logged_in']:
    main_app() # Si ha iniciado sesión, muestra la aplicación principal
else:
    login_form() # Si no ha iniciado sesión, muestra el formulario de login