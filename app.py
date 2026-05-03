import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# 2. FUNÇÃO PARA CARREGAR DADOS DO CSV
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('cidades_rs.csv')
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df_rs = carregar_dados()

# 3. ESTILO CSS PARA PDF (ESCONDE INTERFACE NA IMPRESSÃO)
st.markdown("""
    <style>
    @media print {
        /* Esconde elementos de navegação e inputs no PDF */
        .stButton, .stSlider, .stNumberInput, .stSelectbox, .stHeader, 
        header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] {
            display: none !important;
        }
        .main {
            background-color: white !important;
        }
        /* Ajusta margens para o papel A4 */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    }
    
    /* Estilização do Botão para parecer uma ferramenta profissional */
    div.stButton > button:first-child {
        background-color: #1E3A8A;
        color: white;
        border-radius: 5px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. CABEÇALHO DA PROPOSTA
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>AJC SOLUÇÕES EM ENERGIA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Simulação de Geração Fotovoltaica Personalizada</p>", unsafe_allow_html=True)

if not df_rs.empty:
    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📍 Localização")
        cidade_sel = st.selectbox("Selecione o Município:", df_rs['cidade'].sort_values())
        dados = df_rs[df_rs['cidade'] == cidade_sel].iloc[0]
        tarifa = st.number_input("Tarifa (R$/kWh)", value=1.02)

    with c2:
        st.subheader("⚙️ Sistema")
        potencia = st.number_input("Capacidade Total (kWp)", value=5.5)
        pr = st.slider("Eficiência (PR)", 0.70, 0.90, 0.80)

    # 5. CÁLCULOS
    fatores = [1.28, 1.12, 1.05, 0.82, 0.65, 0.58, 0.62, 0.75, 0.88, 1.02, 1.15, 1.25]
    geracao_base = potencia * dados['hsp'] * pr * 30.4
    geracao_mensal = [round(geracao_base * f, 2) for f in fatores]
    
    # Regra GD2 2026
    tarifa_liq = tarifa - ((tarifa * dados['fio_b']) * 0.60)
    economia_mensal = [round(g * tarifa_liq, 2) for g in geracao_mensal]

    # 6. RESULTADOS
    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    r1.metric("Geração Média", f"{np.mean(geracao_mensal):.2f} kWh")
    r2.metric("Economia Anual", f"R$ {sum(economia_mensal):.2f}")
    r3.metric("Concessionária", dados['concessionaria'])

    # 7. GRÁFICO
    st.bar_chart(pd.DataFrame({"Geração (kWh)": geracao_mensal}, index=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]))

    # 8. BOTÃO PARA SALVAR PDF
    st.markdown("---")
    if st.button("📄 GERAR PROPOSTA EM PDF"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    st.caption(f"Documento gerado para a cidade de {cidade_sel} em {pd.Timestamp.now().strftime('%d/%m/%Y')}")
