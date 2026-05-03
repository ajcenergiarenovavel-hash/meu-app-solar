import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Configuração da Página
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# --- BASE DE DADOS SOLAR E REGRAS DE CONCESSIONÁRIA (GD2 2026) ---
base_solar = {
    "Porto Alegre": {"hsp": [5.21, 5.02, 4.35, 3.50, 2.75, 2.25, 2.45, 3.10, 3.75, 4.45, 5.15, 5.45], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Canoas": {"hsp": [5.20, 5.00, 4.30, 3.45, 2.70, 2.20, 2.40, 3.05, 3.70, 4.40, 5.10, 5.40], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Gravataí": {"hsp": [5.18, 4.98, 4.28, 3.48, 2.72, 2.22, 2.42, 3.08, 3.72, 4.42, 5.12, 5.42], "concessionaria": "RGE Sul", "fio_b": 0.32},
    "Caxias do Sul": {"hsp": [5.10, 4.85, 4.15, 3.30, 2.60, 2.15, 2.30, 2.95, 3.60, 4.30, 4.95, 5.30], "concessionaria": "RGE Sul", "fio_b": 0.32},
    "Encruzilhada do Sul": {"hsp": [5.40, 5.20, 4.50, 3.65, 2.90, 2.40, 2.60, 3.25, 3.90, 4.60, 5.30, 5.60], "concessionaria": "RGE Sul", "fio_b": 0.32},
}

geolocator = Nominatim(user_agent="ajc_solar_sim")

# --- FUNÇÕES DE APOIO ---
def buscar_por_nome(nome_cidade):
    try:
        location = geolocator.geocode(nome_cidade, timeout=10)
        if location: return location.latitude, location.longitude
        return None, None
    except: return None, None

def identificar_cidade(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        addr = location.raw.get('address', {})
        return addr.get('city') or addr.get('town') or addr.get('village') or "Porto Alegre"
    except: return "Porto Alegre"

# --- INTERFACE DO APP ---

# Cabeçalho com Ícone Fotovoltaico e Título
col_icon, col_title = st.columns([1, 5])
with col_icon:
    # Ícone representando Sol + Painel (remetendo à imagem solicitada)
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; background-color: #f0f2f6; border-radius: 20px; padding: 10px;">
            <span style="font-size: 70px;">☀️</span>
            <span style="font-size: 50px; margin-left: -20px; margin-top: 30px;">🟦</span>
        </div>
    """, unsafe_index=True)
    # Alternativamente, se preferir uma imagem de ícone externa:
    # st.image("https://cdn-icons-png.flaticon.com/512/3026/3026360.png", width=120)

with col_title:
    st.title("Simulador de Geração Solar AJC Soluções em Energia")
    st.caption("Cálculo de economia com compensação de crédito e encargo do Fio B (GD2 - 2026)")

st.markdown("---")

c1, c2 = st.columns(2)

with c1:
    st.subheader("📍 Localização e Tarifa")
    cid_input = st.text_input("Cidade para cálculo:", value="Porto Alegre")
    
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat = st.number_input("Latitude", value=st.session_state.get('lat', -30.0325), format="%.6f")
    with col_lon:
        lon = st.number_input("Longitude", value=st.session_state.get('lon', -51.2257), format="%.6f")
    
    if st.button("📍 Sincronizar Localidade"):
        lat_b, lon_b = buscar_por_nome(cid_input)
        if lat_b:
            st.session_state['lat'], st.session_state['lon'] = lat_b, lon_b
            st.session_state['cidade'] = cid_input
            st.rerun()

    tarifa_cheia = st.number_input("Tarifa atual da conta (R$/kWh):", value=1.02, step=0.01)

with c2:
    st.subheader("⚙️ Configuração do Sistema Proposto")
    cc1, cc2 = st.columns(2)
    p_painel = cc1.number_input("Potência do Painel (Wp):", value=550)
    qtd_painel = cc2.number_input("Quantidade de Placas:", value=10)
    
    potencia_total_kwp = (p_painel * qtd_painel) / 1000
    st.info(f"**Capacidade Instalada:** {potencia_total_kwp:.2f} kWp")
    
    pr = st.slider("Eficiência Estimada (Performance Ratio):", 0.70, 0.90, 0.80)

# --- CÁLCULOS TÉCNICOS E FINANCEIROS ---

cidade_ref = st.session_state.get('cidade', identificar_cidade(lat, lon))
dados = base_solar.get(cidade_ref, base_solar["Porto Alegre"])

# Cálculo da Geração
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
geracao_mensal = [round(hsp * potencia_total_kwp * pr * 30.4, 2) for hsp in dados['hsp']]
geracao_media = sum(geracao_mensal) / 12

# Lógica GD2 - 2026: Pagamento de 60% do Fio B
fio_b_valor = tarifa_cheia * dados['fio_b']
encargo_gd2 = fio_b_valor * 0.60 
tarifa_com_desconto = tarifa_cheia - encargo_gd2
economia_mensal = [round(g * tarifa_com_desconto, 2) for g in geracao_mensal]

# --- EXIBIÇÃO DE RESULTADOS ---

st.divider()

# 1. RESUMO DE GERAÇÃO
st.subheader("📊 Resumo de Geração")
res_gen_1, res_gen_2 = st.columns(2)
with res_gen_1:
    st.metric("Geração Média Mensal", f"{geracao_media:.2f} kWh")
with res_gen_2:
    st.metric("Geração Total Anual", f"{sum(geracao_mensal):.2f} kWh")

st.markdown("---")

# 2. INFORMAÇÕES DA CONCESSIONÁRIA E GD2
st.subheader("⚡ Concessionária e Regras de Crédito")
m1, m2, m3 = st.columns(3)
m1.metric("Concessionária", dados['concessionaria'])
m2.metric("Localidade Ref.", cidade_ref)
m3.metric("Valor do Crédito (GD2)", f"R$ {tarifa_com_desconto:.2f}/kWh")

st.success(f"💰 **Economia Anual Líquida Estimada: R$ {sum(economia_mensal):.2f}**")

# Tabela e Gráfico
tab_col, graph_col = st.columns([1, 2])

with tab_col:
    st.write("**Detalhamento Mensal**")
    df_res = pd.DataFrame({
        "Mês": meses,
        "Geração (kWh)": geracao_mensal,
        "Economia (R$)": economia_mensal
    })
    st.dataframe(df_res, hide_index=True)

with graph_col:
    st.write("**Curva de Geração Mensal**")
    st.bar_chart(df_res.set_index("Mês")["Geração (kWh)"])

st.markdown("---")
st.caption("Simulador AJC Soluções em Energia - Base de dados CRESESB / Lei 14.300.")
