import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Base simplificada CRESESB com médias mensais (kWh/m2.dia)
# Nota: Em um cenário real, você pode expandir esta lista ou carregar um CSV
base_cresesb = {
    "Porto Alegre": [5.21, 5.02, 4.35, 3.50, 2.75, 2.25, 2.45, 3.10, 3.75, 4.45, 5.15, 5.45],
    "Canoas": [5.20, 5.00, 4.30, 3.45, 2.70, 2.20, 2.40, 3.05, 3.70, 4.40, 5.10, 5.40],
    "Gravataí": [5.18, 4.98, 4.28, 3.48, 2.72, 2.22, 2.42, 3.08, 3.72, 4.42, 5.12, 5.42],
    "Encruzilhada do Sul": [5.40, 5.20, 4.50, 3.65, 2.90, 2.40, 2.60, 3.25, 3.90, 4.60, 5.30, 5.60],
    "São Paulo": [5.05, 4.90, 4.20, 3.80, 3.30, 3.10, 3.25, 3.75, 4.05, 4.40, 4.95, 5.00],
}

geolocator = Nominatim(user_agent="solar_app_assis_v4")

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

st.title("☀️ Calculadora Solar: Dimensionamento e Geração Mensal")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Localização e Tarifa")
    cidade_input = st.text_input("Digite o nome da cidade", value="Porto Alegre")
    if st.button("Buscar por Nome"):
        lat_busca, lon_busca = buscar_por_nome(cidade_input)
        if lat_busca:
            st.session_state['lat'] = lat_busca
            st.session_state['lon'] = lon_busca
            st.session_state['cidade'] = cidade_input
            st.success(f"Coordenadas encontradas para {cidade_input}")
        else:
            st.error("Cidade não encontrada.")

    st.write("---")
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
    st.info(f"**Potência Total:** {potencia_total_w / 1000:.2f} kWp")
    pr = st.slider("Eficiência (Performance Ratio)", 0.70, 0.90, 0.80)

if 'cidade' in st.session_state:
    cidade_ref = st.session_state['cidade']
    # Busca a lista de irradiação mensal. Se não houver, usa Porto Alegre como base.
    hsp_mensal = base_cresesb.get(cidade_ref, base_cresesb["Porto Alegre"])
    
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    geracao_kwh = []
    economia_brl = []

    for hsp in hsp_mensal:
        # Cálculo: (P_Wp / 1000) * HSP * PR * 30.4 dias
        gen = (potencia_total_w / 1000) * hsp * pr * 30.4
        geracao_kwh.append(round(gen, 2))
        economia_brl.append(round(gen * tarifa, 2))

    df_geracao = pd.DataFrame({
        "Mês": meses,
        "Geração (kWh)": geracao_kwh,
        "Economia (R$)": economia_brl
    })

    st.divider()
    
    # Métricas principais
    m1, m2, m3 = st.columns(3)
    m1.metric("Localidade", cidade_ref)
    m2.metric("Geração Média Mensal", f"{sum(geracao_kwh)/12:.1f} kWh")
    m3.metric("Economia Anual Total", f"R$ {sum(economia_brl):.2f}")

    # Tabela de Geração Mensal
    st.subheader("📊 Tabela de Geração Mensal")
    st.table(df_geracao)

    # Gráfico
    st.subheader("Gráfico de Geração Mensal (kWh)")
    st.bar_chart(df_geracao.set_index("Mês")["Geração (kWh)"])
