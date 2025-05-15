import streamlit as st
import pandas as pd
import os
from sklearn.metrics.pairwise import euclidean_distances

# --- Configuración de página ---
st.set_page_config(page_title="Jugadores similares", layout="wide")
st.subheader("Búsqueda de jugadores similares")

# --- Mapeo de atributos por puesto ---
atributos_por_puesto = {
    "Defensores centrales": [
        'Gol y Finalización', 'Asistencias y creación de chances', '1v1 en ataque',
        'Progresion de pelota', 'Juego asociado', 'Juego aéreo', '1v1 en defensa', 'Defensa'
    ],
    "Laterales": [
        'Gol y Finalización', 'Asistencias y creación de chances', '1v1 en ataque',
        'Centros', 'Juego asociado', 'Juego aéreo', '1v1 en defensa', 'Defensa'
    ],
    "Volantes defensivos": [
        'Gol y Finalización', 'Asistencias y creación de chances', '1v1 en ataque',
        'Progresion de pelota', 'Juego asociado', 'Juego aéreo', '1v1 en defensa', 'Defensa'
    ],
    "Volantes mixtos": [
        'Gol y Finalización','Asistencias y creación de chances',
        '1v1 en ataque', 'Centros', 'Juego asociado', 'Juego aéreo', 'Defensa'
    ],
    "Volantes ofensivos": [
        'Gol y Finalización','Asistencias y creación de chances',
        '1v1 en ataque', 'Centros', 'Juego asociado', 'Juego aéreo', 'Defensa'
    ],
    "Extremos": [
        'Gol y Finalización', 'Asistencias y creación de chances', '1v1 en ataque',
        'Centros', 'Juego asociado', 'Juego aéreo', 'Defensa'
    ],
    "Centrodelanteros": [
        'Gol y Finalización', 'Asistencias y creación de chances', '1v1 en ataque',
        'Centros', 'Juego asociado', 'Juego aéreo', 'Defensa'
    ]
}



# --- Cargar CSV y preparar datos ---
puestos = list(atributos_por_puesto.keys())
puesto_seleccionado = st.selectbox("Seleccioná el puesto:", puestos)
archivo = f"data/{puesto_seleccionado.lower()}.csv"

# --- Cargar CSV y preparar datos ---
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip()

    st.markdown("#### ⏱️ Filtro mínimo de minutos jugados")
    min_minutos = st.number_input("Minutos jugados mínimos:", min_value=0, value=0)
    df = df[df['Minutes played'] >= min_minutos]

    # Crear columna "Jugador con equipo"
    df['Jugador con equipo'] = df['Player'] + ' (' + df['Team within selected timeframe'] + ')'

    atributos_default = atributos_por_puesto[puesto_seleccionado]

    # Selección de jugador
    jugador_nombres = sorted(df['Jugador con equipo'].dropna().unique().tolist())
    jugador_seleccionado = st.selectbox("Seleccioná un jugador de referencia:", jugador_nombres)

    # Filtro por ligas
    st.markdown("#### 🌍 Seleccioná en qué ligas buscar jugadores similares")
    ligas_disponibles = sorted(df['Liga'].dropna().unique().tolist())
    ligas_seleccionadas = st.multiselect("Ligas:", ["Sin asignar"] + ligas_disponibles, default=["Sin asignar"])

    if "Sin asignar" in ligas_seleccionadas:
        df_filtrado = df.copy()
    else:
        df_filtrado = df[df['Liga'].isin(ligas_seleccionadas)]
    
    # Filtro por atributos
    st.markdown("#### 📊 Seleccioná qué atributos usar para comparar")
    atributos_seleccionados = st.multiselect("Atributos:", ["Sin asignar"] + atributos_default, default=["Sin asignar"])

# Si no seleccionan atributos o dejan "Sin asignar", se usan todos los atributos por defecto
    if "Sin asignar" in atributos_seleccionados or not atributos_seleccionados:
        atributos_seleccionados = atributos_default

    if jugador_seleccionado and atributos_seleccionados and ligas_seleccionadas:
        # Aplicar filtros
        df_filtrado = df[df['Liga'].isin(ligas_seleccionadas)]
        df_filtrado = df_filtrado.dropna(subset=atributos_seleccionados)

        # Validar existencia del jugador en el dataframe filtrado
        # Asegurarse de que el jugador esté en el dataset original
        df_referencia = df[df['Jugador con equipo'] == jugador_seleccionado]

        if df_referencia.empty:
            st.warning("⚠️ No se encontró el jugador seleccionado.")
            st.stop()

# Extraer el vector del jugador seleccionado
        vector_referencia = df_referencia[atributos_seleccionados].values[0]

        # Preparar matriz de similitud
        X = df_filtrado[atributos_seleccionados].values
        nombres = df_filtrado['Jugador con equipo'].values
        if df_filtrado.empty:
            st.warning("⚠️ No hay jugadores disponibles para comparar con los filtros seleccionados.")
            st.stop()
        distancias = euclidean_distances([vector_referencia], df_filtrado[atributos_seleccionados].values)[0]

        resultados = df_filtrado.copy()
        resultados['Distancia'] = distancias

        # Excluir al jugador original
        resultados = resultados[resultados['Jugador con equipo'] != jugador_seleccionado]
        resultados = resultados.sort_values("Distancia")

        # Mostrar
        st.markdown("### 🔎 Jugadores más similares")
        columnas_mostrar = ['Jugador con equipo', 'Age', 'Passport country', 'Distancia']
        st.dataframe(resultados[columnas_mostrar].reset_index(drop=True), use_container_width=True)
    else:
        st.info("📝 Seleccioná un jugador, al menos un atributo y una liga para comenzar.")
else:
    st.error("No se encontró el archivo CSV correspondiente al puesto seleccionado.")
