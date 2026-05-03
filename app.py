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

def buscar_cidade_por_coordenada(lat, lon):
    try:
        geolocator = Nominatim(user_agent="solar_app_assis")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        address = location.raw.get('address', {})
        return address.get('city') or address.get('town') or address.get('village') or "Porto Alegre"
    except:
        return "Porto Alegre"

st.set_page_config(page_title="Dimensionamento Solar Profissional", layout="wide", page_icon="☀️")

st.title("☀️ Calculadora Solar: Dimensionamento e Economia")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Localização e Tarifa")
    lat = st.number_input("Latitude", value=-30.0325, format="%.6f")
    lon = st.number_input("Longitude", value=-51.2257, format="%.6f")
    tarifa = st.number_input("Valor da Tarifa (R$/kWh)", value=0.95, step=0.01)
    
    if st.button("📍 Identificar Localidade"):
        cidade = buscar_cidade_por_coordenada(lat, lon)
        st.session_state['cidade'] = cidade

with col2:
    st.subheader("⚙️ Configuração do Sistema")
    
    # NOVOS CAMPOS: Potência da Placa e Quantidade
    col_placa, col_qtd = st.columns(2)
    with col_placa:
        p_painel = st.number_input("Potência do Painel (Wp)", value=550, step=10)
    with col_qtd:
        qtd_painel = st.number_input("Quantidade de Placas", value=10, step=1)
    
    # Cálculo automático da potência total
    potencia_total_w = p_painel * qtd_painel
    st.info(f"**Potência Total do Sistema:** {potencia_total_w / 1000:.2f} kWp")
    
    pr = st.slider("Eficiência (Performance Ratio)", 0.70, 0.90, 0.80, help="Padrão de mercado é 0.80 (80%)")

if 'cidade' in st.session_state:
    cidade_ref = st.session_state['cidade']
    hsp = base_cresesb.get(cidade_ref, {"hsp": 4.42})["hsp"]
    
    # Cálculos
    geracao_diaria = (potencia_total_w / 1000) * hsp * pr
    geracao_mensal = geracao_diaria * 30.4
    economia_mensal = geracao_mensal * tarifa
    economia_anual = economia_mensal * 12

    st.divider()
    
    # Resultados em destaque
    res1, res2, res3 = st.columns(3)
    with res1:
        st.metric("Local Detectado", cidade_ref)
    with res2:
        st.metric("Geração Estimada", f"{geracao_mensal:.1f} kWh/mês")
    with res3:
        st.metric("Economia Mensal", f"R$ {economia_mensal:.2f}")

    st.success(f"💰 **Economia anual estimada com {qtd_painel} placas de {p_painel}Wp: R$ {economia_anual:.2f}**")

    # Gráfico de Projeção Acumulada
    st.subheader("Projeção de Economia Acumulada (12 meses)")
    dados_grafico = pd.DataFrame({
        "Mês": [f"Mês {i}" for i in range(1, 13)],
        "Economia (R$)": [economia_mensal * i for i in range(1, 13)]
    })
    st.area_chart(dados_grafico.set_index("Mês"))
