import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# 2. BASE DE DADOS (Cidades solicitadas e principais do RS)
@st.cache_data
def carregar_dados():
    data = {
        "cidade": [
            "Porto Alegre", "Caxias do Sul", "Canoas", "Pelotas", "Santa Maria", 
            "Gramado", "Canela", "São Francisco de Paula", "Itati", "Terra de Areia", 
            "Torres", "Capão da Canoa", "Xangri-lá", "Atlântida", "Tapes", 
            "Barra do Ribeiro", "São Lourenço do Sul", "Pântano Grande"
        ],
        "lat": [
            -30.0325, -29.1678, -29.9189, -31.7654, -29.6842, 
            -29.3746, -29.3621, -29.4478, -29.4582, -29.5855, 
            -29.3400, -29.7547, -29.8025, -29.7914, -30.6732, 
            -30.2902, -31.3653, -30.1872
        ],
        "lon": [
            -51.2257, -51.1794, -51.1781, -52.3376, -53.8069, 
            -50.8764, -50.8142, -50.5841, -50.1119, -50.0634, 
            -49.7200, -50.0152, -50.0468, -50.0305, -51.3965, 
            -51.3005, -51.9772, -52.3735
        ],
        "hsp": [
            4.42, 4.15, 4.40, 4.35, 4.40, 
            4.12, 4.10, 4.08, 4.05, 4.15, 
            4.12, 4.18, 4.10, 4.10, 4.35, 
            4.38, 4.30, 4.45
        ],
        "concessionaria": [
            "CEEE Equatorial", "RGE Sul", "CEEE Equatorial", "CEEE Equatorial", "RGE Sul",
            "RGE Sul", "RGE Sul", "RGE Sul", "CEEE Equatorial", "CEEE Equatorial",
            "CEEE Equatorial", "CEEE Equatorial", "CEEE Equatorial", "CEEE Equatorial", "CEEE Equatorial",
            "CEEE Equatorial", "CEEE Equatorial", "RGE Sul"
        ],
        "fio_b": [
            0.28, 0.32, 0.28, 0.28, 0.32,
            0.32, 0.32, 0.32, 0.28, 0.28,
            0.28, 0.28, 0.28, 0.28, 0.28,
            0.28, 0.28, 0.32
        ]
    }
    return pd.DataFrame(data)

df_rs = carregar_dados()

# 3. CABEÇALHO
col_icon, col_title = st.columns([0.5, 5.5])
with col_icon:
    st.markdown("<h1 style='font-size: 70px; margin-top: -10px;'>☀️</h1>", unsafe_allow_html=True)

with col_title:
    st.title("Simulador de Geração Solar AJC Soluções em Energia")
    st.caption("Cálculo de economia com Fio B (Regras GD2 - 2026)")

st.markdown("---")

# 4. INPUTS DO UTILIZADOR
c1, c2 = st.columns(2)

with c1:
    st.subheader("📍 Localização do Projeto")
    cidade_selecionada = st.selectbox("Selecione o Município do RS:", df_rs['cidade'].sort_values())
    dados_cidade = df_rs[df_rs['cidade'] == cidade_selecionada].iloc[0]
    
    st.info(f"**Coordenadas GPS:** Latitude: {dados_cidade['lat']} | Longitude: {dados_cidade['lon']}")
    tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

with c2:
    st.subheader("⚙️ Dados do Sistema")
    cc1, cc2 = st.columns(2)
    p_painel = cc1.number_input("Potência do Painel (Wp)", value=550)
    qtd_painel = cc2.number_input("Quantidade de Painéis", value=10)
    potencia_total_kwp = (p_painel * qtd_painel) / 1000
    st.info(f"**Capacidade Instalada:** {potencia_total_kwp:.2f} kWp")
    pr = st.slider("Eficiência Estimada (PR)", 0.70, 0.90, 0.80)

# 5. CÁLCULOS TÉCNICOS (Sazonalidade e GD2)
fatores_mensais = [1.28, 1.12, 1.05, 0.82, 0.65, 0.58, 0.62, 0.75, 0.88, 1.02, 1.15, 1.25]
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

hsp_anual = dados_cidade['hsp']
geracao_base = potencia_total_kwp * hsp_anual * pr * 30.4
geracao_mensal_kwh = [round(geracao_base * f, 2) for f in fatores_mensais]

# Regra GD2 - 2026 (Pagamento de 60% do Fio B)
fio_b_perc = dados_cidade['fio_b']
encargo_gd2 = (tarifa * fio_b_perc) * 0.60
tarifa_liquida = tarifa - encargo_gd2
economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal_kwh]

# 6. EXIBIÇÃO DE RESULTADOS
st.divider()
st.subheader("📊 Resumo de Geração")
r1, r2, r3 = st.columns(3)
r1.metric("Geração Média Mensal", f"{np.mean(geracao_mensal_kwh):.2f} kWh")
r2.metric("Geração Total Anual", f"{sum(geracao_mensal_kwh):.2f} kWh")
r3.metric("Economia Anual Estimada", f"R$ {sum(economia_mensal):.2f}")

st.markdown("---")
st.subheader("⚡ Detalhamento Mensal e Gráfico")

t_col, g_col = st.columns([1, 2])

with t_col:
    df_result = pd.DataFrame({
        "Mês": meses,
        "Geração (kWh)": geracao_mensal_kwh,
        "Economia (R$)": economia_mensal
    })
    st.dataframe(df_result, hide_index=True, use_container_width=True)

with g_col:
    st.bar_chart(df_result.set_index("Mês")["Geração (kWh)"])

st.markdown("---")
m1, m2, m3 = st.columns(3)
m1.metric("Concessionária", dados_cidade['concessionaria'])
m2.metric("Cidade Referência", cidade_selecionada)
m3.metric("Valor do Crédito Líquido", f"R$ {tarifa_liquida:.2f}")

# 7. FUNÇÃO DE IMPRESSÃO
st.markdown("""
    <style>
    @media print {
        .stButton, header, footer { display: none !important; }
        .main { background-color: white !important; }
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("🖨️ Imprimir Proposta / Gerar PDF"):
    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

st.caption("Simulador AJC Soluções em Energia | Dados: CRESESB | Regras: Lei 14.300")
