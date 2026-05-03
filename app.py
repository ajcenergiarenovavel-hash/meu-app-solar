import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# 1. Configuração da Página (Deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# 2. Inicialização do Estado (Evita erros de variáveis inexistentes)
if 'lat' not in st.session_state:
    st.session_state['lat'] = -30.0325
if 'lon' not in st.session_state:
    st.session_state['lon'] = -51.2257
if 'cidade' not in st.session_state:
    st.session_state['cidade'] = "Porto Alegre"

# 3. Base de Dados Solar e Concessionárias (GD2 - Regras de 2026)
base_solar = {
    "Porto Alegre": {"hsp": [5.21, 5.02, 4.35, 3.50, 2.75, 2.25, 2.45, 3.10, 3.75, 4.45, 5.15, 5.45], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Canoas": {"hsp": [5.20, 5.00, 4.30, 3.45, 2.70, 2.20, 2.40, 3.05, 3.70, 4.40, 5.10, 5.40], "concessionaria": "CEEE Equatorial", "fio_b": 0.28},
    "Gravataí": {"hsp": [5.18, 4.98, 4.28, 3.48, 2.72, 2.22, 2.42, 3.08, 3.72, 4.42, 5.12, 5.42], "concessionaria": "RGE Sul", "fio_b": 0.32},
    "Caxias do Sul": {"hsp": [5.10, 4.85, 4.15, 3.30, 2.60, 2.15, 2.30, 2.95, 3.60, 4.30, 4.95, 5.30], "concessionaria": "RGE Sul", "fio_b": 0.32},
    "Encruzilhada do Sul": {"hsp": [5.40, 5.20, 4.50, 3.65, 2.90, 2.40, 2.60, 3.25, 3.90, 4.60, 5.30, 5.60], "concessionaria": "RGE Sul", "fio_b": 0.32},
}

geolocator = Nominatim(user_agent="ajc_solar_app_v5")

# 4. Funções de Localização com Tratamento de Erros
def buscar_por_nome(nome):
    try:
        location = geolocator.geocode(nome, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception:
        return None, None

def identificar_cidade(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        if location:
            addr = location.raw.get('address', {})
            return addr.get('city') or addr.get('town') or addr.get('village') or "Porto Alegre"
        return "Porto Alegre"
    except Exception:
        return "Porto Alegre"

# 5. Interface - Cabeçalho
col_icon, col_title = st.columns([1, 5])
with col_icon:
    # Ícone representativo de energia solar
    st.image("https://cdn-icons-png.flaticon.com/512/4049/4049757.png", width=120)

with col_title:
    st.title("Simulador de Geração Solar AJC Soluções em Energia")
    st.caption("Análise Técnica de Geração e Economia com Cálculo de Fio B (Regras GD2 - 2026)")

st.markdown("---")

# 6. Inputs do Usuário
c1, c2 = st.columns(2)

with c1:
    st.subheader("📍 Localização e Tarifa")
    nome_cidade = st.text_input("Buscar cidade por nome:", value=st.session_state['cidade'])
    
    if st.button("🔍 Buscar e Atualizar"):
        lat_n, lon_n = buscar_por_nome(nome_cidade)
        if lat_n:
            st.session_state['lat'], st.session_state['lon'] = lat_n, lon_n
            st.session_state['cidade'] = nome_cidade
            st.success(f"Localizado: {nome_cidade}")
            st.rerun()
        else:
            st.error("Cidade não encontrada. Tente um nome mais específico.")

    st.write("---")
    lat_input = st.number_input("Latitude", value=st.session_state['lat'], format="%.6f")
    lon_input = st.number_input("Longitude", value=st.session_state['lon'], format="%.6f")
    tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

with c2:
    st.subheader("⚙️ Dados do Sistema")
    cc1, cc2 = st.columns(2)
    p_painel = cc1.number_input("Potência Unitária do Painel (Wp)", value=550)
    qtd_painel = cc2.number_input("Quantidade de Painéis", value=10)
    
    potencia_total_kwp = (p_painel * qtd_painel) / 1000
    st.info(f"**Capacidade Instalada Total:** {potencia_total_kwp:.2f} kWp")
    
    pr = st.slider("Eficiência Estimada (Performance Ratio)", 0.70, 0.90, 0.80)

# 7. Cálculos de Geração e Financeiro
dados_local = base_solar.get(st.session_state['cidade'], base_solar["Porto Alegre"])

# Sazonalidade Mensal
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
geracao_mensal = [round(hsp * potencia_total_kwp * pr * 30.4, 2) for hsp in dados_local['hsp']]
geracao_media = sum(geracao_mensal) / 12

# Regra GD2 2026 (Pagamento de 60% do Fio B sobre o excedente)
# Para simplificação comercial, aplicamos sobre a geração total
fio_b_perc = dados_local['fio_b']
valor_fio_b = tarifa * fio_b_perc
custo_gd2_2026 = valor_fio_b * 0.60
tarifa_liquida = tarifa - custo_gd2_2026
economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal]

# 8. Exibição dos Resultados
st.divider()

# Bloco 1: Resumo de Geração (Conforme solicitado)
st.subheader("📊 Resumo de Geração em kWh")
res1, res2 = st.columns(2)
res1.metric("Geração Média Mensal", f"{geracao_media:.2f} kWh")
res2.metric("Geração Total Anual", f"{sum(geracao_mensal):.2f} kWh")

st.markdown("---")

# Bloco 2: Dados Financeiros e Concessionária
st.subheader("⚡ Detalhes Financeiros e Concessionária")
m1, m2, m3 = st.columns(3)
m1.metric("Concessionária", dados_local['concessionaria'])
m2.metric("Cidade Referência", st.session_state['cidade'])
m3.metric("Valor do Crédito Líquido", f"R$ {tarifa_liquida:.2f}")

st.success(f"💰 **Economia Líquida Estimada para o Primeiro Ano: R$ {sum(economia_mensal):.2f}**")

# Tabela e Gráfico
t_col, g_col = st.columns([1, 2])

with t_col:
    st.write("**Geração Mês a Mês**")
    df = pd.DataFrame({
        "Mês": meses,
        "Geração (kWh)": geracao_mensal,
        "Economia (R$)": economia_mensal
    })
    st.dataframe(df, hide_index=True)

with g_col:
    st.write("**Comportamento da Geração no Ano**")
    st.bar_chart(df.set_index("Mês")["Geração (kWh)"])

st.markdown("---")
st.caption("Simulador AJC Soluções em Energia | Dados: CRESESB | Regras: Lei 14.300 (GD2 - 2026)")
