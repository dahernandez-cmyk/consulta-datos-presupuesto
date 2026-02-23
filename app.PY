import streamlit as st
import pandas as pd

st.set_page_config(page_title="Presupuesto Gasto Personal", page_icon="💰", layout="wide")

st.title("🚀 Sistema de Presupuesto y Distribución")

# --- 1. MEMORIA DE SESIÓN ---
if 'vacantes' not in st.session_state:
    st.session_state['vacantes'] = []

# --- 2. CARGA DE ARCHIVOS ---
st.info("💡 **PASO 1:** Cargue los archivos de Excel para habilitar los filtros y cálculos.")
col_a, col_b = st.columns(2)
with col_a:
    archivo_dist = st.file_uploader("1. Sube Distribución (.xlsx)", type=["xlsx"])
with col_b:
    archivo_detalle = st.file_uploader("2. Sube Detalle Empleados (.xlsx)", type=["xlsx"])

# --- 3. PROCESAMIENTO ---
if archivo_dist and archivo_detalle:
    try:
        # Carga de datos
        df_dist = pd.read_excel(archivo_dist, sheet_name="Datos", dtype={"IdCentroCosto": str, "IdEmpleado": str, "Identificacion": str})
        #df_empl = pd.read_excel(archivo_detalle, sheet_name="Datos Empleado", dtype={"Identificacion": str})
        df_empl_raw = pd.read_excel(archivo_detalle, sheet_name="Datos Empleado", dtype={"Identificacion": str})
        df_empl = df_empl_raw[df_empl_raw["EstadoContrato"] == "Activo"].copy()

        df_pagos = pd.read_excel(archivo_detalle, sheet_name="DatosPagosFijos", dtype={"Identificacion": str, "IdItem": str})
        
        # Diccionario de Nóminas para el formulario
        df_nominas_ref = df_empl[["Nomina", "DescripcionNomina"]].drop_duplicates().dropna()
        # Limpieza de Nomina para el diccionario
        df_nominas_ref["Nomina"] = df_nominas_ref["Nomina"].astype(str).str.replace(".0", "", regex=False).str.strip()
        dict_nominas = dict(zip(df_nominas_ref["DescripcionNomina"], df_nominas_ref["Nomina"]))
        lista_nombres_nomina = sorted(list(dict_nominas.keys()))

        # --- FORMULARIO DE VACANTES ---
        st.sidebar.header("➕ Agregar Vacante")
        with st.sidebar.form("vacante_form"):
            v_id = st.text_input("ID Identificación", "VAC001")
            v_nom = st.text_input("Nombre Completo", "VACANTE")
            v_desc_nomina = st.selectbox("Descripción Nómina", options=lista_nombres_nomina)
            v_car = st.text_input("Cargo", "ANALISTA")
            v_cc_i = st.text_input("ID Centro Costo (8 dígitos)", "10101001")
            v_cc_n = st.text_input("Nombre Centro Costo", "CENTRO")
            
            v_riesgo_clase = st.selectbox("Clase de Riesgo", 
                                        options=["Clase I", "Clase IV", "Clase V"], 
                                        index=0)
            
            v_ds = st.number_input("% Distribución", value=100.0)
            v_sl = st.number_input("Salario", value=0)
            v_fl = st.number_input("Flexible", value=0)
            v_de = st.number_input("Desalarizado", value=0)
            
            if st.form_submit_button("Añadir Vacante"):
                id_seleccionado = dict_nominas[v_desc_nomina]
                st.session_state['vacantes'].append({
                    "Identificacion": v_id, "NombreCompleto": v_nom, "Nomina": id_seleccionado,
                    "DescripcionNomina": v_desc_nomina, "Cargo": v_car, "IdCentroCosto": v_cc_i, 
                    "CentroCosto": v_cc_n, "PorcentajeDistribucion": v_ds, "Salario": v_sl,
                    "Total Flexible": v_fl, "Total Desalarizado": v_de, 
                    "ClaseDeRiesgo": v_riesgo_clase, "Promedio Comisiones": 0
                })
                st.rerun()

        # Cálculos de Pagos Fijos
        df_f = df_pagos[df_pagos["IdItem"].isin(["P689", "P809", "P694", "P690", "P688", "B03", "B09", "B02", "EN02", "EN01"])].groupby("Identificacion")["Valor"].sum().reset_index().rename(columns={"Valor": "Total Flexible"})
        df_d = df_pagos[df_pagos["IdItem"].isin(["B01", "P691", "P695"])].groupby("Identificacion")["Valor"].sum().reset_index().rename(columns={"Valor": "Total Desalarizado"})

        # Cruce Maestro
        df_e = df_empl[["Identificacion", "Nomina", "DescripcionNomina", "ClaseDeRiesgo", "Cargo", "Salario", "Promedio Comisiones"]].drop_duplicates("Identificacion")
        df = pd.merge(df_dist, df_e, on="Identificacion", how="left")
        df = pd.merge(df, df_f, on="Identificacion", how="left")
        df = pd.merge(df, df_d, on="Identificacion", how="left")

        # Unir Vacantes
        if st.session_state['vacantes']:
            df = pd.concat([df, pd.DataFrame(st.session_state['vacantes'])], ignore_index=True)

        # --- APLICACIÓN DE FILTROS ---
        df["IdCentroCosto"] = df["IdCentroCosto"].astype(str)
        df = df[df["IdCentroCosto"].str[4].isin(["1", "2", "3", "4"])].copy()
        df = df[~df["CentroCosto"].str.contains("FORMALETAS", case=False, na=False)]
        df = df[~df["Cargo"].str.strip().isin(["AUXILIAR GESTION DE NEGOCIOS DEI", "ANALISTA GESTION DE NEGOCIOS DEI"])]

        # Filtro UIV Medellín Operativa
        cond_uiv = ((df["CentroCosto"].str.strip() == "UIV ELECTICA MEDELLÍN") & (df["DescripcionNomina"].str.strip() == "NOMINA OPERATIVA"))
        df = df[~cond_uiv].copy()

        # --- CÁLCULOS ECONÓMICOS ---
        cols_num = ["Salario", "Total Flexible", "Total Desalarizado", "Promedio Comisiones"]
        df[cols_num] = df[cols_num].fillna(0)
        df["Salario Total"] = df["Salario"] + df["Total Flexible"] + df["Total Desalarizado"]
        
        smmlv_2026 = 1750905
        df["Exonerado"] = df["Salario Total"].apply(lambda x: "No Exonerado" if x > (smmlv_2026 * 10) else "Exonerado")
        
        # --- NORMALIZACIÓN DE NÓMINA PARA CÁLCULO DE PROVISIÓN ---
        df["Nomina"] = df["Nomina"].astype(str).str.replace(".0", "", regex=False).str.strip()

        def calc_prov_sin_arl(row):
            nom = row["Nomina"]
            exo = row["Exonerado"]
            if nom in ["1", "4"]: return 39.77 if exo == "Exonerado" else 53.27
            elif nom == "3": return 28.70
            elif nom == "2": return 47.77
            elif nom == "5": return 14.44
            return 0.0

        df["Provision Sin Arl"] = df.apply(calc_prov_sin_arl, axis=1)

        def calc_riesgo(row):
            clase = str(row["ClaseDeRiesgo"])
            nom = row["Nomina"]
            if "Clase V" in clase: base = 6.960
            elif "Clase IV" in clase: base = 4.350
            else: base = 0.522 
            return base * 0.70 if nom == "3" else base
            
        df["Riesgo"] = df.apply(calc_riesgo, axis=1)
        df["Provision %"] = df["Riesgo"] + df["Provision Sin Arl"]

        # Auxilio Transporte
        df["Auxilio Transporte"] = df.apply(lambda r: 253118 if (r["Salario Total"] + r["Promedio Comisiones"]) <= (smmlv_2026 * 2) else 0, axis=1)
        
        if df["PorcentajeDistribucion"].max() <= 1: df["PorcentajeDistribucion"] *= 100
        df["Sueldos"] = df["Salario Total"] * (df["PorcentajeDistribucion"] / 100)

        # --- FORMATEO MANUAL A TEXTO ---
        for col in ["Salario", "Total Flexible", "Total Desalarizado", "Salario Total", "Sueldos", "Promedio Comisiones", "Auxilio Transporte"]:
            df[col + "_V"] = df[col].apply(lambda x: f"$ {x:,.0f}")
        
        df["Dist_V"] = df["PorcentajeDistribucion"].apply(lambda x: f"{x:.2f}%")
        df["Riesgo_V"] = df["Riesgo"].apply(lambda x: f"{x:.3f}%")
        df["ProvSinArl_V"] = df["Provision Sin Arl"].apply(lambda x: f"{x:.2f}%")
        df["Provision_V"] = df["Provision %"].apply(lambda x: f"{x:.2f}%")

        # Visualización Final
        orden = [
            "Nomina", "DescripcionNomina", "Identificacion", "NombreCompleto", "Cargo",
            "IdCentroCosto", "CentroCosto", "ClaseDeRiesgo", "Dist_V", "Riesgo_V",
            "Salario_V", "Total Flexible_V", "Total Desalarizado_V", "Salario Total_V", 
            "Exonerado", "ProvSinArl_V", "Provision_V", "Sueldos_V", "Promedio Comisiones_V", "Auxilio Transporte_V"
        ]
        
        df_mostrar = df[orden].rename(columns={c: c.replace("_V", "") for c in orden})

        st.subheader("📊 Tabla de Presupuesto Consolidada")
        st.dataframe(df_mostrar, hide_index=True)

    except Exception as e:
        st.error(f"Error detectado: {e}")
else:
    st.warning("👈 Cargue los archivos para ver los resultados.")

if st.sidebar.button("🗑️ Limpiar Vacantes"):
    st.session_state['vacantes'] = []
    st.rerun()