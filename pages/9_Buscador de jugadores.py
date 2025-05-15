import streamlit as st
import pandas as pd
import os

# --- Configuración inicial ---
st.set_page_config(page_title="Buscador por perfil")
st.title("🎯 Buscador de jugadores por perfil")

# --- Mapas de atributos por puesto ---
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

# --- Selección del puesto ---

puestos = list(atributos_por_puesto.keys())
puesto_seleccionado = st.selectbox("Seleccioná el puesto a analizar:", puestos)
archivo = f"../data/{puesto_seleccionado}.csv"


# --- Cargar datos ---
if os.path.exists(archivo):
    df = pd.read_csv(archivo)

    # Crear columna "Jugador con equipo"
    df['Jugador con equipo'] = df['Player'] + ' (' + df['Team within selected timeframe'] + ')'

    # --- Filtros condicionales ---
    col1, col2, col3 = st.columns(3)

    with col1:
        if puesto_seleccionado not in ["Laterales", "Extremos"]:
            pierna = st.selectbox("Pierna hábil:", ["Sin asignar"] + sorted(df['Foot'].dropna().unique().tolist()))
            if pierna != "Sin asignar":
                df = df[df['Foot'] == pierna]
        elif puesto_seleccionado == "Laterales":
            lateral = st.selectbox("Puesto:", ["Sin asignar", "Lateral derecho (RB)", "Lateral izquierdo (LB)"])
            if lateral == "Lateral derecho (RB)":
                df = df[df['Position'].str.contains('R', na=False)]
            elif lateral == "Lateral izquierdo (LB)":
                df = df[df['Position'].str.contains('L', na=False)]
        elif puesto_seleccionado == "Extremos":
            extremo = st.selectbox("Puesto:", ["Sin asignar", "Extremo por derecha", "Extremo por izquierda"])
            if extremo == "Extremo por derecha":
                df = df[df['Position'].str.contains('R', na=False)]
            elif extremo == "Extremo por izquierda":
                df = df[df['Position'].str.contains('L', na=False)]

        # Agregar filtro de pierna hábil para extremos
            pierna = st.selectbox("Pierna hábil:", ["Sin asignar"] + sorted(df['Foot'].dropna().unique().tolist()), key="foot_extremos")
            if pierna != "Sin asignar":
                df = df[df['Foot'] == pierna]

    with col2:
        opciones_ligas = ["Sin asignar"] + sorted(df['Liga'].dropna().unique().tolist())
        ligas_seleccionadas = st.multiselect("Liga (puede seleccionar varias):", opciones_ligas, default=["Sin asignar"])

        if "Sin asignar" not in ligas_seleccionadas and ligas_seleccionadas:
            df = df[df['Liga'].isin(ligas_seleccionadas)]

    with col3:
        min_minutos = st.number_input("Minutos jugados mínimos:", min_value=0, value=0)
        df = df[df['Minutes played'] >= min_minutos]

    

    st.markdown("### 📊 Filtros por atributos específicos del puesto")
    atributos = atributos_por_puesto[puesto_seleccionado]

    # --- Sliders de atributos ---
    sliders = {}
    for atributo in atributos:
        min_val = int(df[atributo].min())
        max_val = int(df[atributo].max())
        sliders[atributo] = st.slider(f"{atributo}:", min_val, max_val, (min_val, max_val))

    # --- Aplicar filtros por atributos ---
    for atributo, (min_val, max_val) in sliders.items():
        df = df[df[atributo].between(min_val, max_val)]

    st.markdown("### 🧾 Jugadores que cumplen con los criterios")
    columnas_resultado = ['Jugador con equipo', 'Age', 'Passport country'] + atributos
    st.dataframe(df[columnas_resultado], use_container_width=True)
else:
    st.error("No se encontró el archivo CSV correspondiente.")
