import streamlit as st
import pandas as pd

# -------------------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL Y USUARIOS (FUERA DE CUALQUIER FUNCIÓN)
# -------------------------------------------------------------------------

# Inicializa las variables de sesión al inicio del script
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

# Definición de Usuarios (Diccionario)
USUARIOS = {
    "jose.d": "pass123",     
    "companero1": "seguro456",
    "admin": "admin2026"
}

# -------------------------------------------------------------------------
# 2. FUNCIÓN DE INICIO DE SESIÓN (LOGIN PAGE)
# -------------------------------------------------------------------------

def login_form():
    """Muestra el formulario de inicio de sesión."""
    # ⬇️ Indentación obligatoria de 4 espacios a partir de aquí
    st.title("🔐 Iniciar Sesión")
    st.subheader("Acceso a Consulta de Valores")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Ingresar")

    if submit_button:
        if username in USUARIOS and USUARIOS[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
    # ⬆️ FIN DE LA FUNCIÓN login_form()

# -------------------------------------------------------------------------
# 3. FUNCIÓN DE CONTENIDO PRINCIPAL (MAIN APP PAGE)
# -------------------------------------------------------------------------

def main_app():
    """Contenido principal de la aplicación (Filtros y Tabla)."""
    # ⬇️ Indentación obligatoria de 4 espacios a partir de aquí
    
    # ⚠️ PUNTO DE CONTROL: CARGA DE DATOS (DEBE ESTAR DENTRO DE main_app)
    try:
        df = pd.read_csv('prueba.csv', sep=';', encoding='latin-1')
        df.columns = df.columns.str.strip()
    except Exception as e:
        # Si falla en la nube, muestra el error y sale de la función
        st.error(f"❌ Error al cargar el archivo CSV: {e}")
        return 
        
    st.title('Sistema de Consulta de Presupuesto Gasto de Personal 2026')
    
    # Botón de Cerrar Sesión
    st.sidebar.markdown(f"**Usuario:** {st.session_state['username']}")
    if st.sidebar.button("🔓 Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.rerun()

    # ------------------- Lógica de Filtros (Tu código) -------------------
    st.sidebar.header('Opciones de Filtro')
    nombres_disponibles = df['Nombre'].unique()
    
    seleccionar_todo = st.sidebar.checkbox(
        "✅ Seleccionar todos los nombres", 
        value=True
    )
    
    if seleccionar_todo:
        lista_predeterminada = nombres_disponibles
    else:
        lista_predeterminada = []

    nombre_seleccionado = st.sidebar.multiselect(
        'Selecciona el Nombre:',
        options=nombres_disponibles,
        default=lista_predeterminada
    )
    
    # Aplicar el filtro final
    df_filtrado = df[df['Nombre'].isin(nombre_seleccionado)]

    # Mostrar los resultados
    st.dataframe(df_filtrado)
    st.markdown(f"Mostrando **{len(df_filtrado)}** de **{len(df)}** registros.")
    # ⬆️ FIN DE LA FUNCIÓN main_app()

# -------------------------------------------------------------------------
# 4. LÓGICA DE NAVEGACIÓN PRINCIPAL (FLUJO DEL PROGRAMA)
# -------------------------------------------------------------------------

# Esto se ejecuta cada vez que se carga la página
if st.session_state['logged_in']:
    main_app()
else:
    login_form()