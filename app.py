import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Simulação da base SunData (CRESESB)
base_cresesb = {
    "Porto Alegre": {"hsp": 4.42, "lat": -30.03},
    "Canoas": {"hsp": 4.40, "lat": -29.91},
    "Gravataí": {"hsp": 4.38, "lat": -29.94},
    "Encruzilhada do Sul": {"hsp": 4.55, "lat": -30.54}
}

def buscar_cidade_por_coordenada(lat, lon):
    try:
        geolocator = Nominatim(user_agent="solar_app_v2")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        address = location.raw.get('address', {})
        return address.get('city') or address.get('town') or address.get('village') or "Porto Alegre"
    except:
        return "Porto Alegre"

st.set_page_config(page_title="Calculadora de Economia Solar", layout="wide")

st.title("☀️ Calculadora Solar & Estimativa de Economia")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Localização e Tarifas")
    lat = st.number_input("Latitude", value=-30.0325, format="%.6f")
    lon = st.number_input("Longitude", value=-51.2257, format="%.6f")
    
    # NOVO: Campo de Tarifa de Energia
    tarifa = st.number_input("Valor da Tarifa Vigente (R$/kWh)", value=0.95, step=0.01, help="Consulte o valor do kWh na sua conta de luz (incluindo impostos).")
    
    if st.button("Identificar Localidade"):
        cidade = buscar_cidade_por_coordenada(lat, lon)
        st.session_state['cidade'] = cidade

with col2:
    st.subheader("🛠️ Especificações do Sistema")
    potencia_w = st.number_input("Potência Total Instalada (Wp)", value=5000, step=100)
    pr = st.slider("Eficiência do Sistema (PR)", 0.70, 0.90, 0.80)

if 'cidade' in st.session_state:
    cidade_ref = st.session_state['cidade']
    # Busca HSP na base
    hsp = base_cresesb.get(cidade_ref, base_cresesb["Porto Alegre"])["hsp"]
    
    # Cálculos Técnicos
    geracao_diaria = (potencia_w / 1000) * hsp * pr
    geracao_mensal = geracao_diaria * 30.4
    
    # Cálculos Financeiros
    economia_mensal = geracao_mensal * tarifa
    economia_anual = economia_mensal * 12

    st.divider()
    
    # Exibição de Resultados em Cards
    m1, m2, m3 = st.columns(3)
    m1.metric("Localidade", cidade_ref)
    m2.metric("Geração Mensal", f"{geracao_mensal:.1f} kWh")
    m3.metric("Economia Mensal Est.", f"R$ {economia_mensal:.2f}")

    st.success(f"💰 **Economia Estimada no Primeiro Ano: R$ {economia_anual:.2f}**")

    # Gráfico de Projeção Simples (12 meses)
    dados_grafico = pd.DataFrame({
        "Mês": range(1, 13),
        "Economia Acumulada (R$)": [economia_mensal * i for i in range(1, 13)]
    })
    st.line_chart(dados_grafico.set_index("Mês"))
