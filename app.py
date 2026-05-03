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
            st.session_state['lat'] = lat_busca
            st.session_state['lon'] = lon_busca
            st.session_state['cidade'] = cidade_input
            st.success(f"Coordenadas encontradas para {cidade_input}")
        else:
            st.error("Cidade não encontrada. Verifique o nome.")

    st.write("--- ou use as coordenadas ---")
    
    # Campos de Coordenadas (com valores persistentes)
    lat = st.number_input("Latitude", value=st.session_state.get('lat', -30.0325), format="%.6f", key="lat_input")
    lon = st.number_input("Longitude", value=st.session_state.get('lon', -51.2257), format="%.6f", key="lon_input")
    
    if st.button("📍 Identificar Localidade por Coordenadas"):
        cidade_detectada = buscar_por_coordenadas(lat, lon)
        st.session_state['cidade'] = cidade_detectada
        st.session_state['lat'] = lat
        st.session_state['lon'] = lon
        st.success(f"Local identificado: {cidade_detectada}")

    tarifa = st.number_input("Valor da Tarifa (R$/kWh)", value=0.95, step=0.01)

with col2:
    st.subheader("⚙️ Configuração do Sistema")
    
    col_placa, col_qtd = st.columns(2)
    with col_placa:
        p_painel = st.number_input("Potência do Painel (Wp)", value=550, step=10)
    with col_qtd:
        qtd_painel = st.number_input("Quantidade de Placas", value=10, step=1)
    
    potencia_total_w = p_painel * qtd_painel
    st.info(f"**Potência Total do Sistema:** {potencia_total_w / 1000:.2f} kWp")
    
    pr = st.slider("Eficiência (Performance Ratio)", 0.70, 0.90, 0.80)

# Lógica de cálculo baseada na cidade definida
if 'cidade' in st.session_state:
    cidade_ref = st.session_state['cidade']
    # Busca HSP na base (usa Porto Alegre como fallback se a cidade não estiver na lista fixa)
    hsp = base_cresesb.get(cidade_ref, {"hsp": 4.42})["hsp"]
    
    geracao_diaria = (potencia_total_w / 1000) * hsp * pr
    geracao_mensal = geracao_diaria * 30.4
    economia_mensal = geracao_mensal * tarifa
    economia_anual = economia_mensal * 12

    st.divider()
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Local de Referência", cidade_ref)
    res2.metric("Geração Estimada", f"{geracao_mensal:.1f} kWh/mês")
    res3.metric("Economia Mensal", f"R$ {economia_mensal:.2f}")

    st.success(f"💰 **Economia anual estimada: R$ {economia_anual:.2f}**")
    
    st.subheader("Projeção de Economia Acumulada (12 meses)")
    dados_grafico = pd.DataFrame({
        "Mês": [f"Mês {i}" for i in range(1, 13)],
        "Economia (R$)": [economia_mensal * i for i in range(1, 13)]
    })
    st.area_chart(dados_grafico.set_index("Mês"))
