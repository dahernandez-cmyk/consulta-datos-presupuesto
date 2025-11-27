import streamlit as st
import pandas as pd

# Intenta leer con punto y coma y latin-1
# Si tienes problemas de tokenizing, recuerda usar sep=';' si ese es tu delimitador
try:
    df = pd.read_csv('prueba.csv', sep=';', encoding='latin-1')
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"Error al cargar el archivo CSV: {e}")
    st.stop() # Detiene la ejecución si hay un error de lectura



st.title('Sistema de Consulta de Presupuesto Gasto de Personal 2026')

# ----------------------------------------------------
# 2. Diseño de la Interfaz y Filtros
# ----------------------------------------------------


# Crea el contenedor para los filtros en la barra lateral
st.sidebar.header('Opciones de Filtro')

# Paso A: Crear el filtro 'NombreCompleto' usando st.multiselect
nombres_disponibles = df['Nombre'].unique()

nombre_seleccionado = st.sidebar.multiselect(
    'Selecciona el Nombre:',
    options=nombres_disponibles,
    # Por defecto, selecciona todos los nombres
    default=nombres_disponibles
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

