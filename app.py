import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Base de Dados Solar e Concessionárias
base_solar = {
    "Porto Alegre": {"hsp": [5.21, 5.02, 4.35, 3.50, 2.75, 2.25, 2.45, 3.10, 3.75, 4.45, 5.15, 5.45], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Canoas": {"hsp": [5.20, 5.00, 4.30, 3.45, 2.70, 2.20, 2.40, 3.05, 3.70, 4.40, 5.10, 5.40], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Gravataí": {"hsp": [5.18, 4.98, 4.28, 3.48, 2.72, 2.22, 2.42, 3.08, 3.72, 4.42, 5.12, 5.42], "concessionaria": "RGE Sul", "fio_b": 0.32},
    "Encruzilhada do Sul": {"hsp": [5.40, 5.20, 4.50, 3.65, 2.90, 2.40, 2.60, 3.25, 3.90, 4.60, 5.30, 5.60], "concessionaria": "RGE Sul", "fio_b": 0.32},
}

geolocator = Nominatim(user_agent="solar_app_pro_2026")

def identificar_local(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        addr = location.raw.get('address', {})
        cidade = addr.get('city') or addr.get('town') or addr.get('village') or "Porto Alegre"
        return cidade
    except:
        return "Porto Alegre"

st.set_page_config(page_title="Simulador Solar GD2 - 2026", layout="wide", page_icon="☀️")

st.title("☀️ Simulador Solar Profissional (Regras GD2 - 2026)")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Localização e Tarifa")
    lat = st.number_input("Latitude", value=-30.0325, format="%.6f")
    lon = st.number_input("Longitude", value=-51.2257, format="%.6f")
    tarifa_cheia = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)
    
    if st.button("📍 Identificar Local e Concessionária"):
        st.session_state['cidade'] = identificar_local(lat, lon)

with col2:
    st.subheader("⚙️ Configuração do Sistema")
    c1, c2 = st.columns(2)
    p_painel = c1.number_input("Potência do Painel (Wp)", value=550)
    qtd_painel = c2.number_input("Qtd. de Painéis", value=10)
    potencia_total = (p_painel * qtd_painel) / 1000
    pr = st.slider("Eficiência do Sistema (PR)", 0.70, 0.90, 0.80)
    st.info(f"**Potência Total:** {potencia_total:.2f} kWp")

if 'cidade' in st.session_state:
    cidade = st.session_state['cidade']
    dados = base_solar.get(cidade, base_solar["Porto Alegre"])
    
    # Regra GD2 - Ano 2026 (60% do Fio B)
    fio_b_perc = dados['fio_b']
    pagamento_fio_b = (tarifa_cheia * fio_b_perc) * 0.60
    tarifa_liquida = tarifa_cheia - pagamento_fio_b

    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    geracao_lista = [round(hsp * potencia_total * pr * 30.4, 2) for hsp in dados['hsp']]
    economia_lista = [round(g * tarifa_liquida, 2) for g in geracao_lista]

    st.divider()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Concessionária", dados['concessionaria'])
    m2.metric("Cidade", cidade)
    m3.metric("Valor do Crédito (GD2)", f"R$ {tarifa_liquida:.2f}")

    st.warning(f"ℹ️ **Nota Legal (Maio/2026):** Cálculo considera o pagamento de 60% do Fio B sobre a energia injetada.")

    # Tabela de Resultados
    df = pd.DataFrame({"Mês": meses, "Geração (kWh)": geracao_lista, "Economia (R$)": economia_lista})
    
    c_tab, c_graph = st.columns([1, 2])
    with c_tab:
        st.subheader("📊 Geração Mensal")
        st.table(df)
    with c_graph:
        st.subheader("📈 Projeção de Geração")
        st.bar_chart(df.set_index("Mês")["Geração (kWh)"])

    st.success(f"💰 **Economia anual líquida estimada: R$ {sum(economia_lista):.2f}**")
