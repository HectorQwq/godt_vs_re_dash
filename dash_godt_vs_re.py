import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# ---------------------------
# CONFIGURACIÓN DE CONEXIÓN
# ---------------------------
def get_connection():
    return psycopg2.connect(
        host="pg-2e98ffe3-akarius001-83bb.i.aivencloud.com",
        dbname="defaultdb",
        user="avnadmin",
        password="AVNS_JA4bRWb9PGAUAJUDtMZ",
        port=27399
    )

# ---------------------------
# CONSULTA GENÉRICA
# ---------------------------
def load_table(query):
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de conexión o consulta: {e}")
        return pd.DataFrame()

# ---------------------------
# CONFIGURACIÓN STREAMLIT
# ---------------------------
st.set_page_config(page_title="Dashboard RENIEC & GODT", layout="wide")
st.title("🧬 Dashboard RENIEC & GODT")
st.markdown("Este dashboard muestra datos analíticos sobre la intención y efectividad de la donación de órganos.")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("📌 Selecciona el análisis")
tipo = st.sidebar.radio("Tipo de análisis:", [
    "RENIEC Nacional (Preguntas 1-9)",
    "Comparativa Internacional GODT"
])

# ---------------------------
# RENIEC NACIONAL
# ---------------------------
if tipo == "RENIEC Nacional (Preguntas 1-9)":
    preguntas = {
        "1. Proporción Donantes por Departamento (Perú)": "SELECT * FROM mat_01_departamentos_mayor_proporcion ORDER BY proporcion_donantes_pct DESC",
        "2. Menor Proporción por Departamento (Perú)": "SELECT * FROM mat_01_departamentos_mayor_proporcion ORDER BY proporcion_donantes_pct ASC",
        "3. Donación por Continente": "SELECT * FROM tres_donacion_por_continente ORDER BY porcentaje_donantes DESC",
        "4. Donación por País": "SELECT * FROM cuatro_donacion_por_pais ORDER BY porcentaje_donantes DESC",
        "5. Donación por Departamento (Perú)": "SELECT * FROM cinco_donacion_por_departamento ORDER BY porcentaje_donantes DESC",
        "6. Donación por Sexo": "SELECT * FROM seis_donacion_por_sexo ORDER BY porcentaje_donantes DESC",
        "7. Donación por Grupo Etario": "SELECT * FROM siete_donacion_por_edad ORDER BY porcentaje_donantes DESC",
        "8. Rechazo por Edad": "SELECT * FROM ocho_rechazo_por_edad ORDER BY edad",
        "9. Educación por Departamento": "SELECT * FROM nueve_educacion_por_departamento ORDER BY porcentaje_aceptacion ASC"
    }
    pregunta = st.selectbox("Selecciona una pregunta RENIEC:", list(preguntas.keys()))
    df = load_table(preguntas[pregunta])
    st.subheader("📋 Tabla de Resultados")
    st.dataframe(df, use_container_width=True)

    posibles_columnas = [col for col in df.columns if col.startswith("porcentaje") or col.startswith("proporcion")]
    col_valor = posibles_columnas[0] if posibles_columnas else df.columns[1]
    col_etiqueta = df.columns[0]

    st.subheader("📊 Gráfico de Barras")
    fig = px.bar(
        df, x=col_etiqueta, y=col_valor, text=col_valor, color=col_valor,
        labels={col_valor: "Porcentaje (%)", col_etiqueta: col_etiqueta.capitalize()},
        title=pregunta, color_continuous_scale="Tealgrn"
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, height=600)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# ---------------------------
# COMPARATIVA INTERNACIONAL
# ---------------------------
else:
    seccion = st.selectbox("Selecciona comparativa GODT:", [
        "1. Intención vs Realidad (Perú vs Mundo)",
        "2. Brecha Perú: Intención vs Donantes Efectivos",
        "3. ICIE: Conversión de Intención en Donación",
        "4. Donación Exitosa en Vivo",
        "5. Índice de Donación Mundial"
    ])

    if seccion.startswith("1"):
        st.header("📊 Intención de Donar vs Donación Efectiva (RENIEC vs GODT)")
        df = load_table("SELECT * FROM comparativa_tasa_donacion ORDER BY tasa_intencion_reniec DESC")
        st.dataframe(df, use_container_width=True)

        # Corregir columna size para el gráfico
        df["total_donantes_godt"] = pd.to_numeric(df["total_donantes_godt"], errors="coerce").fillna(0)

        fig = px.scatter(
            df,
            x="pais",
            y="tasa_intencion_reniec",
            size="total_donantes_godt",
            color="continente",
            title="Tasa de Intención vs Donantes Efectivos (PM)",
            size_max=60
        )
        st.plotly_chart(fig, use_container_width=True)

    elif seccion.startswith("2"):
        st.header("📉 Brecha de Donación en Perú")
        df = load_table("SELECT * FROM godtdos_donacion_peru")
        st.dataframe(df, use_container_width=True)
        st.plotly_chart(
            px.bar(df, x="pais", y="brecha_tasa_donacion", color="brecha_tasa_donacion",
                   title="Brecha RENIEC - GODT por millón"),
            use_container_width=True
        )

    elif seccion.startswith("3"):
        st.header("📈 Índice de Conversión ICIE")
        df = load_table("SELECT * FROM comparativa_icie ORDER BY icie DESC")
        st.dataframe(df, use_container_width=True)
        st.plotly_chart(
            px.bar(df, x="pais", y="icie", color="icie", title="Índice ICIE por país"),
            use_container_width=True
        )

    elif seccion.startswith("4"):
        st.header("💉 Donación Exitosa en Vivo")
        df = load_table("SELECT * FROM godtcuatro_donacion_vivo ORDER BY total_donaciones_vivo DESC")
        st.dataframe(df, use_container_width=True)
        st.plotly_chart(
            px.bar(df, x="pais", y="total_donaciones_vivo", color="continente",
                   title="Total Donaciones en Vivo por País"),
            use_container_width=True
        )

    elif seccion.startswith("5"):
        st.header("🌐 Índice Mundial de Donación por Millón")
        df = load_table("SELECT * FROM indicecinco_donacion_mundial ORDER BY indice_donacion_pm DESC")
        st.dataframe(df, use_container_width=True)
        st.plotly_chart(
            px.bar(df, x="pais", y="indice_donacion_pm", color="indice_donacion_pm",
                   title="Donación por Millón de Personas (PM)"),
            use_container_width=True
        )
