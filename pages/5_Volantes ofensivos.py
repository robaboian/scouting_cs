import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Radar
from matplotlib.patheffects import withStroke

# Cargar el CSV
@st.cache_data
def load_data():
    return pd.read_csv('data/volantes ofensivos.csv')

# App principal
def main():
    st.set_page_config(page_title="Volantes ofensivos", layout="wide")
    st.subheader("Volantes ofensivos")

    df = load_data()


    df['Perfil ofensivo'] = (df['Gol y Finalización']*0.2 + df['Asistencias y creación de chances']*0.2 +
                             df['1v1 en ataque']*0.2 + df['Centros']*0.1 +
                             df['Juego asociado']*0.25 + df['Juego aéreo']*0.05).astype(int)

    df['Perfil defensivo'] = (df['Defensa']*0.8 +
                              df['Juego aéreo']*0.2).astype(int)

    # Filtros de minutos jugados
    min_minutos = int(df['Minutes played'].min())
    max_minutos = int(df['Minutes played'].max())
    minutos = st.slider(
        "Filtrar por minutos jugados (solo se mostrarán jugadores dentro del rango):",
        min_value=min_minutos, max_value=max_minutos,
        value=(min_minutos, max_minutos)
    )

    # Filtro por pierna hábil
    opciones_pierna = ['Sin aclarar'] + sorted(df['Foot'].dropna().unique())
    pierna = st.selectbox("Filtrar por pierna hábil:", opciones_pierna)


    # Filtro por país
    ligas = ['Sin aclarar'] + sorted(df['Liga'].dropna().unique())
    liga = st.selectbox("Filtrar por liga:", ligas)

        # Aplicación de los filtros
    df = df[(df['Minutes played'] >= minutos[0]) & (df['Minutes played'] <= minutos[1])]

    if pierna != 'Sin aclarar':
        f = df[df['Foot'].isin([pierna, 'both', 'unknown'])]
    
    if liga != 'Sin aclarar':
        df = df[df['Liga'] == liga]

    df['Jugador con equipo'] = df['Player'] + ' (' + df['Team within selected timeframe'] + ')'

    jugadores = df['Jugador con equipo'].unique()
    jugador_1 = st.selectbox('Selecciona el primer jugador:', jugadores, key='jugador1')
    jugadores_opcionales = ['Ninguno'] + list(jugadores[jugadores != jugador_1])
    jugador_2 = st.selectbox('Selecciona el segundo jugador (opcional):', jugadores_opcionales, key='jugador2')

    nombre_jugador_1 = jugador_1.split(' (')[0]
    nombre_jugador_2 = jugador_2.split(' (')[0] if jugador_2 != 'Ninguno' else None

    
    data_jugador_1 = df[df['Jugador con equipo'] == jugador_1]
    data_jugador_2 = df[df['Jugador con equipo'] == jugador_2] if jugador_2 != 'Ninguno' else None

    datos_radar = [
        'Gol y Finalización','Asistencias y creación de chances',
        '1v1 en ataque', 'Centros', 'Juego asociado', 'Juego aéreo', 'Defensa']

    radar = Radar(
        params=datos_radar,
        min_range=[df[col].min() for col in datos_radar],
        max_range=[df[col].max() for col in datos_radar]
    )

    fig, ax = radar.setup_axis(figsize=(15, 15), facecolor='#191e2a')
    fig.patch.set_facecolor('#191e2a')
    radar.draw_circles(ax=ax, facecolor="#191e2a", edgecolor='pink', lw=1.5)

    values_1 = list(data_jugador_1[datos_radar].iloc[0].astype(float).values)

    if data_jugador_2 is not None:
        values_2 = list(data_jugador_2[datos_radar].iloc[0].astype(float).values)

        radar.draw_radar_compare(
            ax=ax,
            values=values_1,
            compare_values=values_2,
            kwargs_compare={
                'facecolor': '#23a88b',
                'alpha': 0.6,
                'edgecolor': 'yellow',
                'lw': 2,
                'linestyle': '-'
            },
            kwargs_radar={
                'facecolor': '#19687f',
                'alpha': 0.8,
                'edgecolor': 'white',
                'lw': 2,
                'linestyle': '-'
            }
        )
    else:
        radar.draw_radar(
            ax=ax,
            values=values_1,
            kwargs_radar={
                'facecolor': '#19687f',
                'alpha': 0.8,
                'edgecolor': 'white',
                'lw': 2,
                'linestyle': '-',
            }
        )

    radar.draw_range_labels(
        ax=ax,
        fontsize=13,
        weight='bold',
        color='white',
        fontfamily='Verdana',
        path_effects=[withStroke(linewidth=3, foreground='black')]
    )

    radar.draw_param_labels(
        ax=ax,
        fontsize=14,
        color='white',
        fontfamily='Verdana',
        weight='bold',
        offset=0.6,
        path_effects=[withStroke(linewidth=3, foreground='black')]
    )

    equipo_jugador_1 = data_jugador_1['Team within selected timeframe'].values[0]
    texto_jugador_1 = f"{nombre_jugador_1} ({equipo_jugador_1})"

    ax.text(
        0.05, 0.91,
        texto_jugador_1, weight='bold', fontsize=14, fontfamily='Verdana',
        color='#19687f', transform=ax.transAxes,
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.4')
    )

    if data_jugador_2 is not None:
        equipo_jugador_2 = data_jugador_2['Team within selected timeframe'].values[0]
        texto_jugador_2 = f"{nombre_jugador_2} ({equipo_jugador_2})"

        ax.text(
            0.05, 0.95,
            texto_jugador_2, weight='bold', fontsize=14, fontfamily='Verdana',
            color='#23a88b', transform=ax.transAxes,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.4')
        )

    # Mostrar primero el radar
    st.pyplot(fig, use_container_width=False)

    fig2, ax2 = plt.subplots(figsize=(12, 8))
    fig2.patch.set_facecolor('#191e2a')
    ax2.set_facecolor('#191e2a')

    ax2.tick_params(colors='white')
    ax2.xaxis.label.set_color('white')
    ax2.yaxis.label.set_color('white')
    ax2.title.set_color('white')

    ax2.set_xlabel('Perfil Ofensivo', fontsize=14, fontfamily='Verdana')
    ax2.set_ylabel('Perfil Defensivo', fontsize=14, fontfamily='Verdana')
    ax2.set_title('Comparativa entre perfiles de jugadores', fontsize=14, fontfamily='Verdana', weight='bold')

    ax2.spines['bottom'].set_color('white')
    ax2.spines['top'].set_color('white')
    ax2.spines['right'].set_color('white')
    ax2.spines['left'].set_color('white')

    ax2.scatter(df['Perfil ofensivo'], df['Perfil defensivo'], color='lightblue', alpha=0.03)

    if data_jugador_2 is not None:
        ax2.scatter(data_jugador_1['Perfil ofensivo'], data_jugador_1['Perfil defensivo'], color='white', label=texto_jugador_1, s=150, alpha=1,edgecolors="black")
        ax2.scatter(data_jugador_2['Perfil ofensivo'], data_jugador_2['Perfil defensivo'], color='yellow', label=texto_jugador_2, s=150, alpha=1,edgecolors="black")
    else:
        ax2.scatter(data_jugador_1['Perfil ofensivo'], data_jugador_1['Perfil defensivo'], color='white', label=texto_jugador_1, s=150, alpha=1, edgecolors="black")

    legend = ax2.legend(facecolor='#191e2a', edgecolor='white', fontsize=10)
    for text in legend.get_texts():
        text.set_color('white')
        text.set_fontfamily('Verdana')

    st.pyplot(fig2, use_container_width=False)





    # Luego mostrar gráfico comparativo de perfiles
if __name__ == '__main__':
    main()
