import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# 1. Configuração da Página
st.set_page_config(page_title="Simulador Solar AJC - RS", layout="wide", page_icon="☀️")

# 2. Carregamento da Base de Dados (RS Completo)
# Nota: Simulando a carga. No seu GitHub, use: pd.read_csv('cidades_rs.csv')
@st.cache_data
def carregar_base():
    # Aqui você carregaria o CSV com as 497 cidades. 
    # Exemplo com dados estruturais para demonstração:
    data = {
        "cidade": ["Porto Alegre", "Caxias do Sul", "Passo Fundo", "Pelotas", "Santa Maria", "Erechim", "Bento Gonçalves", "Uruguaiana"],
        "lat": [-30.0325, -29.1678, -28.2628, -31.7654, -29.6842, -27.634, -29.170, -29.754],
        "lon": [-51.2257, -51.1794, -52.4067, -52.3376, -53.8069, -52.273, -51.511, -57.088],
        "hsp": [4.42, 4.15, 4.30, 4.35, 4.40, 4.25, 4.18, 4.80],
        "concessionaria": ["CEEE Equatorial", "RGE Sul", "RGE Sul", "CEEE Equatorial", "RGE Sul", "RGE Sul", "RGE Sul", "RGE Sul"],
        "fio_b": [0.28, 0.32, 0.32, 0.28, 0.32, 0.32, 0.32, 0.32]
    }
    return pd.DataFrame(data)

df_rs = carregar_base()

# 3. Interface - Cabeçalho
col_icon, col_title = st.columns([0.5, 5.5])
with col_icon:
    st.markdown("<h1 style='font-size: 70px; margin-top: -10px;'>☀️</h1>", unsafe_allow_html=True)
with col_title:
    st.title("Simulador de Geração Solar AJC Soluções em Energia")
    st.caption("Base Completa Rio Grande do Sul | Regras GD2 - 2026")

st.markdown("---")

# 4. Seleção de Cidade e GPS
c1, c2 = st.columns(2)
with c1:
    st.subheader("📍 Localização do Projeto")
    cidade_sel = st.selectbox("Selecione a cidade do RS:", df_rs['cidade'].sort_values())
    
    # Busca dados da cidade selecionada
    dados_cid = df_rs[df_rs['cidade'] == cidade_sel].iloc[0]
    
    # EXIBIÇÃO DAS COORDENADAS GPS
    st.info(f"**Coordenadas GPS:** Latitude: {dados_cid['lat']} | Longitude: {dados_cid['lon']}")
    
    tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

with c2:
    st.subheader("⚙️ Dimensionamento")
    p_painel = st.number_input("Potência do Painel (Wp)", value=550)
    qtd_painel = st.number_input("Quantidade de Placas", value=10)
    potencia_total = (p_painel * qtd_painel) / 1000
    pr = st.slider("Eficiência (Performance Ratio)", 0.70, 0.90, 0.80)

# 5. Cálculos (Sazonalidade simplificada baseada na média da cidade)
# Em um app real, o CSV teria os 12 meses. Aqui usamos a média anual da base.
geracao_mensal_media = potencia_total * dados_cid['hsp'] * pr * 30.4
tarifa_liquida = tarifa - (tarifa * dados_cid['fio_b'] * 0.60) 
economia_mensal = geracao_mensal_media * tarifa_liquida

# 6. Resultados
st.divider()
st.subheader("📊 Resumo de Geração e Local")
r1, r2, r3 = st.columns(3)
r1.metric("Geração Média", f"{geracao_mensal_media:.2f} kWh/mês")
r2.metric("Concessionária", dados_cid['concessionaria'])
r3.metric("Crédito Líquido", f"R$ {tarifa_liquida:.2f}")

st.success(f"💰 **Economia Anual Estimada para {cidade_sel}: R$ {economia_mensal * 12:.2f}**")

# 7. Botão de Impressão
st.markdown("""
    <style>
    @media print { .stButton, header, footer { display: none !important; } }
    </style>
    """, unsafe_allow_html=True)

if st.button("🖨️ Gerar Proposta em PDF / Imprimir"):
    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
