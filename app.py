import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Base simplificada CRESESB (Sugestão: ampliar com CSV no futuro)
base_cresesb = {
    "Porto Alegre": {"hsp": 4.42},
    "Canoas": {"hsp": 4.40},
    "Gravataí": {"hsp": 4.38},
    "Encruzilhada do Sul": {"hsp": 4.55},
    "São Paulo": {"hsp": 4.25},
    "Cuiabá": {"hsp": 4.95}
}

geolocator = Nominatim(user_agent="solar_app_assis_v3")

def buscar_por_coordenadas(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        address = location.raw.get('address', {})
        return address.get('city') or address.get('town') or address.get('village') or "Porto Alegre"
    except:
        return "Porto Alegre"

def buscar_por_nome(nome_cidade):
    try:
        location = geolocator.geocode(nome_cidade, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except:
        return None, None

st.set_page_config(page_title="Dimensionamento Solar Profissional", layout="wide", page_icon="☀️")

st.title("☀️ Calculadora Solar: Dimensionamento e Economia")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Localização e Tarifa")
    
    # Opção de busca por Nome da Cidade
    cidade_input = st.text_input("Digite o nome da cidade", value="Porto Alegre")
    if st.button("Buscar por Nome"):
        lat_busca, lon_busca = buscar_por_nome(cidade_input)
        if lat_busca:
