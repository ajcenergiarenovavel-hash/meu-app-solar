import streamlit as st
import pandas as pd
import numpy as np
from streamlit_js_eval import get_geolocation, streamlit_js_eval # Adicionado streamlit_js_eval

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# Funções auxiliares para geolocalização
def calcular_distancia(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - np.cos((lat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 12742 * np.arcsin(np.sqrt(a))

# 2. FUNÇÃO PARA CARREGAR DADOS DO CSV
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('cidades_rs.csv')
        return df
    except FileNotFoundError:
        st.error("Erro: O arquivo 'cidades_rs.csv' não foi encontrado no diretório.")
        return pd.DataFrame()

df_rs = carregar_dados()

# 3. CABEÇALHO
col_icon, col_title = st.columns([0.5, 5.5])
with col_icon:
    st.markdown("<h1 style='font-size: 70px; margin-top: -10px;'>☀️</h1>", unsafe_allow_html=True)

with col_title:
    st.title("Simulador de Geração Solar AJC Soluções em Energia")
    st.caption("Cálculo de economia com Fio B (Regras GD2 - 2026)")

st.markdown("---")

if not df_rs.empty:
    # --- BOTÃO DE LOCALIZAÇÃO ---
    st.subheader("📍 Localização do Projeto")
    col_loc1, col_loc2 = st.columns([2, 1])
    
    with col_loc2:
        loc = get_geolocation()
        if st.button("🌐 Detectar minha localização"):
            if loc:
                user_lat = loc['coords']['latitude']
                user_lon = loc['coords']['longitude']
                distancias = df_rs.apply(lambda row: calcular_distancia(user_lat, user_lon, row['lat'], row['lon']), axis=1)
                idx_proxima = distancias.idxmin()
                st.session_state['cidade_detectada'] = df_rs.loc[idx_proxima, 'cidade']
                st.success(f"Localização aproximada detectada: {st.session_state['cidade_detectada']}")
            else:
                st.error("Por favor, permita o acesso à localização no seu navegador.")

    with col_loc1:
        default_index = 0
        lista_cidades = sorted(df_rs['cidade'].unique())
        if 'cidade_detectada' in st.session_state:
            try:
                default_index = lista_cidades.index(st.session_state['cidade_detectada'])
            except ValueError:
                default_index = 0
            
        cidade_selecionada = st.selectbox("Selecione ou confirme o Município:", lista_cidades, index=default_index)

    # 4. RESTANTE DOS INPUTS
    dados_cidade = df_rs[df_rs['cidade'] == cidade_selecionada].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Dados Técnicos Local:** Lat: {dados_cidade['lat']} | Lon: {dados_cidade['lon']} | HSP: {dados_cidade['hsp']}")
        tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

    with c2:
        st.subheader("⚙️ Dados do Sistema")
        cc1, cc2 = st.columns(2)
        p_painel = cc1.number_input("Potência do Painel (Wp)", value=550)
        qtd_painel = cc2.number_input("Quantidade de Painéis", value=10)
        potencia_total_kwp = (p_painel * qtd_painel) / 1000
        pr = st.slider("Eficiência Estimada (PR)", 0.70, 0.90, 0.80)

    # 5. CÁLCULOS TÉCNICOS
    fatores_mensais = [1.28, 1.12, 1.05, 0.82, 0.65, 0.58, 0.62, 0.75, 0.88, 1.02, 1.15, 1.25]
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    hsp_anual = dados_cidade['hsp']
    geracao_base = potencia_total_kwp * hsp_anual * pr * 30.4
    geracao_mensal_kwh = [round(geracao_base * f, 2) for f in fatores_mensais]

    encargo_gd2 = (tarifa * dados_cidade['fio_b']) * 0.60
    tarifa_liquida = tarifa - encargo_gd2
    economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal_kwh]

    # 6. EXIBIÇÃO DE RESULTADOS
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Geração Média Mensal", f"{np.mean(geracao_mensal_kwh):.2f} kWh")
    r2.metric("Geração Total Anual", f"{sum(geracao_mensal_kwh):.2f} kWh")
    r3.metric("Economia Anual Estimada", f"R$ {sum(economia_mensal):.2f}")

    st.markdown("---")
    t_col, g_col = st.columns([1, 2])

    with t_col:
        df_result = pd.DataFrame({"Mês": meses, "Geração (kWh)": geracao_mensal_kwh, "Economia (R$)": economia_mensal})
        st.dataframe(df_result, hide_index=True, use_container_width=True)

    with g_col:
        st.bar_chart(df_result.set_index("Mês")["Geração (kWh)"])

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Concessionária", dados_cidade['concessionaria'])
    m2.metric("Fio B Pago (60%)", f"R$ {encargo_gd2:.3f}")
    m3.metric("Crédito Líquido", f"R$ {tarifa_liquida:.2f}")

    # 7. NOVA FUNÇÃO DE IMPRESSÃO (CORRIGIDA)
    st.markdown("""
        <style>
        @media print {
            .stButton, header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"], .stSelectbox, .stNumberInput, .stSlider { 
                display: none !important; 
            }
            .main { background-color: white !important; }
            .block-container { padding: 0 !important; }
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("📄 Gerar PDF / Imprimir Proposta"):
        streamlit_js_eval(js_expressions="window.print()", want_output=False)

    st.caption("AJC Soluções em Energia | Localização inteligente via GPS")
else:
    st.warning("Carregue o arquivo 'cidades_rs.csv' para continuar.")
