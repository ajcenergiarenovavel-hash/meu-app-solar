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

# 3. CABEÇALHO PROFISSIONAL
st.markdown("""
    <div style='text-align: center; padding: 10px; border-bottom: 2px solid #f0f2f6;'>
        <h1 style='color: #1E3A8A; margin-bottom: 0;'>AJC SOLUÇÕES EM ENERGIA</h1>
        <p style='color: #6B7280; font-size: 1.1em;'>Simulador de Geração Fotovoltaica</p>
    </div>
    """, unsafe_allow_html=True)

if not df_rs.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. ENTRADA DE DADOS
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📍 Localização")
        cidade_selecionada = st.selectbox("Município do RS:", df_rs['cidade'].sort_values())
        dados_cidade = df_rs[df_rs['cidade'] == cidade_selecionada].iloc[0]
        
        st.info(f"**Dados Técnicos:** GPS {dados_cidade['lat']}/{dados_cidade['lon']} | HSP: {dados_cidade['hsp']}")
        tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

    with c2:
        st.subheader("⚙️ Sistema")
        cc1, cc2 = st.columns(2)
        p_painel = cc1.number_input("Painel (Wp)", value=550)
        qtd_painel = cc2.number_input("Quantidade", value=10)
        potencia_total_kwp = (p_painel * qtd_painel) / 1000
        pr = st.slider("Eficiência (PR)", 0.70, 0.90, 0.80)

    # 5. CÁLCULOS DE GERAÇÃO E ECONOMIA
    # Fatores de sazonalidade ordenados de Jan a Dez
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    fatores_mensais = [1.28, 1.12, 1.05, 0.82, 0.65, 0.58, 0.62, 0.75, 0.88, 1.02, 1.15, 1.25]
    
    hsp_anual = dados_cidade['hsp']
    geracao_base = potencia_total_kwp * hsp_anual * pr * 30.4
    
    # Lista de geração e economia
    geracao_mensal_kwh = [round(geracao_base * f, 2) for f in fatores_mensais]
    encargo_gd2 = (tarifa * dados_cidade['fio_b']) * 0.60
    tarifa_liquida = tarifa - encargo_gd2
    economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal_kwh]

    # 6. EXIBIÇÃO DE RESULTADOS
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Geração Média Mensal", f"{np.mean(geracao_mensal_kwh):.2f} kWh")
    r2.metric("Economia Anual Estimada", f"R$ {sum(economia_mensal):.2f}")
    r3.metric("Concessionária", dados_cidade['concessionaria'])

    # 7. GRÁFICO ORGANIZADO POR MESES (JAN-DEZ)
    st.markdown("### 📈 Geração Mensal Estimada (kWh)")
    
    df_grafico = pd.DataFrame({
        "Mês": meses,
        "Geração (kWh)": geracao_mensal_kwh
    })
    
    # O Streamlit mantém a ordem das linhas do DataFrame no gráfico de barras
    st.bar_chart(df_grafico.set_index("Mês"))

    # 8. TABELA DE DETALHAMENTO
    with st.expander("Ver detalhamento mensal em valores"):
        df_result = pd.DataFrame({
            "Mês": meses,
            "Geração (kWh)": geracao_mensal_kwh,
            "Economia (R$)": economia_mensal
        })
        st.table(df_result)

    st.divider()
    st.caption(f"AJC Soluções em Energia | Cálculo baseado na Lei 14.300 (GD2 - 2026)")

else:
    st.error("Arquivo 'cidades_rs.csv' não encontrado. Certifique-se de que ele está no diretório do app.")
