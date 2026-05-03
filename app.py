import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# 1. Configuração da Página
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# 2. Inicialização do Estado
if 'lat' not in st.session_state:
    st.session_state['lat'] = -30.0325
if 'lon' not in st.session_state:
    st.session_state['lon'] = -51.2257
if 'cidade' not in st.session_state:
    st.session_state['cidade'] = "Porto Alegre"

# 3. Base de Dados Solar e Concessionárias (GD2 - 2026)
base_solar = {
    "Porto Alegre": {"hsp": [5.21, 5.02, 4.35, 3.50, 2.75, 2.25, 2.45, 3.10, 3.75, 4.45, 5.15, 5.45], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Canoas": {"hsp": [5.20, 5.00, 4.30, 3.45, 2.70, 2.20, 2.40, 3.05, 3.70, 4.40, 5.10, 5.40], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Gravataí": {"hsp": [5.18, 4.98, 4.28, 3.48, 2.72, 2.22, 2.42, 3.08, 3.72, 4.42, 5.12, 5.42], "concessionaria": "RGE Sul", "fio_b": 0.32},
    "Caxias do Sul": {"hsp": [5.10, 4.85, 4.15, 3.30, 2.60, 2.15, 2.30, 2.95, 3.60, 4.30, 4.95, 5.30], "concessionaria": "RGE Sul", "fio_b": 0.32},
}

geolocator = Nominatim(user_agent="ajc_solar_app_final")

def buscar_por_nome(nome):
    try:
        location = geolocator.geocode(nome, timeout=10)
        if location: return location.latitude, location.longitude
        return None, None
    except: return None, None

# 4. Interface - Cabeçalho (Agora com Ícone de Sol ☀️)
col_icon, col_title = st.columns([0.5, 5.5])
with col_icon:
    st.markdown("<h1 style='font-size: 70px; margin-top: -10px;'>☀️</h1>", unsafe_allow_html=True)

with col_title:
    st.title("Simulador de Geração Solar AJC Soluções em Energia")
    st.caption("Cálculo de economia com Fio B (Regras GD2 - 2026)")

st.markdown("---")

# 5. Inputs
c1, c2 = st.columns(2)
with c1:
    st.subheader("📍 Localização")
    nome_cidade = st.text_input("Cidade:", value=st.session_state['cidade'])
    if st.button("🔍 Atualizar Cidade"):
        lat_n, lon_n = buscar_por_nome(nome_cidade)
        if lat_n:
            st.session_state['lat'], st.session_state['lon'] = lat_n, lon_n
            st.session_state['cidade'] = nome_cidade
            st.rerun()
    
    tarifa = st.number_input("Tarifa (R$/kWh)", value=1.02, step=0.01)

with c2:
    st.subheader("⚙️ Sistema")
    p_painel = st.number_input("Wp do Painel", value=550)
    qtd_painel = st.number_input("Qtd Placas", value=10)
    potencia_total = (p_painel * qtd_painel) / 1000
    pr = st.slider("Eficiência (PR)", 0.70, 0.90, 0.80)

# 6. Cálculos
dados_local = base_solar.get(st.session_state['cidade'], base_solar["Porto Alegre"])
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
geracao_mensal = [round(hsp * potencia_total * pr * 30.4, 2) for hsp in dados_local['hsp']]
tarifa_liquida = tarifa - (tarifa * dados_local['fio_b'] * 0.60) # Regra 2026
economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal]

# 7. Resultados
st.divider()
st.subheader("📊 Resumo de Geração")
r1, r2 = st.columns(2)
r1.metric("Média Mensal", f"{sum(geracao_mensal)/12:.2f} kWh")
r2.metric("Total Anual", f"{sum(geracao_mensal):.2f} kWh")

st.markdown("---")
st.subheader("⚡ Financeiro e Concessionária")
m1, m2, m3 = st.columns(3)
m1.metric("Concessionária", dados_local['concessionaria'])
m2.metric("Cidade", st.session_state['cidade'])
m3.metric("Crédito GD2", f"R$ {tarifa_liquida:.2f}")

st.success(f"💰 **Economia Anual Estimada: R$ {sum(economia_mensal):.2f}**")

# Tabela e Gráfico
t_col, g_col = st.columns([1, 2])
with t_col:
    df = pd.DataFrame({"Mês": meses, "Geração (kWh)": geracao_mensal, "Economia (R$)": economia_mensal})
    st.dataframe(df, hide_index=True)
with g_col:
    st.bar_chart(df.set_index("Mês")["Geração (kWh)"])

st.markdown("---")

# 8. Botão de Imprimir (Final do App)
st.markdown("""
    <style>
    @media print {
        .stButton, .stDownloadButton, header, footer { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("🖨️ Imprimir Proposta / Gerar PDF"):
    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

st.caption("AJC Soluções em Energia | Lei 14.300")
