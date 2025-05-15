import os
import random
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Configuración de la página
st.set_page_config(page_title="Calculadora GBE", layout="centered")
st.subheader("Buscador del GBE")

load_dotenv()
API_KEY = os.getenv("TRANSFERLAB_API_KEY")
SEARCH_URL = "https://transferlabapi.lcp.uk.com/v2/players/searchGbe"

# --- Lista de user-agents para rotar ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Android 10; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0"
]

def get_random_headers():
    return {
        "api_key": API_KEY,
        "User-Agent": random.choice(USER_AGENTS)
    }

# --- Input del usuario ---
st.markdown("#### 🔍 Buscador")
search_string = st.text_input("Ingresá el nombre de un jugador para consultar su elegibilidad GBE:")

if search_string:
    with st.spinner("Buscando jugadores..."):
        try:
            response = requests.get(
                SEARCH_URL,
                params={"searchString": search_string},
                headers=get_random_headers()
            )
            response.raise_for_status()
            players = response.json().get("result", [])
        except Exception as e:
            st.error(f"❌ Error al consultar la API: {e}")
            players = []

    if players:
        options = {f"{p['name']} ({p['club']})": p for p in players}
        selected_label = st.selectbox("🎯 Seleccioná un jugador", list(options.keys()))
        selected_player = options[selected_label]

        st.divider()

        # --- Mostrar información del jugador ---
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(f"https://faimages.lcp.uk.com/players/{selected_player['id']}.png", width=150)

        with col2:
            st.markdown(f"### 📌 {selected_player['name']}")
            st.write(f"**Club:** {selected_player['club']}")
            st.write(f"**Posición:** {selected_player.get('position', 'Desconocida')}")
            st.write(f"**Edad:** {selected_player.get('age', 'No informada')} años")

        st.divider()

        # --- Puntaje y estado ---
        total_score = selected_player.get("totalScore")
        status = selected_player.get("status", "Desconocido")

        st.markdown("#### 🧮 Puntaje GBE")

        if total_score == "Auto Pass" or status == "Auto Pass":
            st.metric("Puntaje total", "Auto Pass")
            st.markdown(
    "<div style='color: #3c763d; background-color: #dff0d8; padding: 1rem; border-radius: 5px; font-size: 1.2rem; font-weight: bold;'>✅ Cumple automáticamente los requisitos del GBE</div>",
    unsafe_allow_html=True
)
        else:
            st.metric("Puntaje total", f"{total_score} puntos")
            if status.lower() == "eligible":
                st.success("✅ Elegible para jugar en el Reino Unido")
            else:
                st.warning("❌ No elegible actualmente")

        # --- Desglose de categorías (comentado por ahora) ---
        # category_data = selected_player.get("categoryScores", {}).get("data", {})
        # if category_data:
        #     st.markdown("### 📊 Desglose por categoría")
        #     table = [
        #         {
        #             "Categoría": cat.replace("_", " ").title(),
        #             "Puntos": info["points"],
        #             "Descripción": info["description"]
        #         }
        #         for cat, info in category_data.items()
        #     ]
        #     df = pd.DataFrame(table)
        #     st.dataframe(df, use_container_width=True)

        st.divider()
    else:
        st.warning("⚠️ No se encontraron jugadores con ese nombre.")
