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
    # Si la casilla está marcada, la lista predeterminada son TODOS los nombres
    lista_predeterminada = nombres_disponibles
else:
    # Si la casilla no está marcada, la lista predeterminada está vacía
    lista_predeterminada = []

# ----------------------------------------------------
# 3. Crear el Filtro Multiselect
# ----------------------------------------------------
nombre_seleccionado = st.sidebar.multiselect(
    'Selecciona el Nombre:',
    options=nombres_disponibles,
    # El valor por defecto se basa en la casilla de arriba
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

