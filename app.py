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
        # Carrega o arquivo consolidado (padrão vírgula e ponto decimal)
        df = pd.read_csv('cidades_rs_completo.csv')
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df_rs = carregar_dados()

# 3. CABEÇALHO PROFISSIONAL COM ÍCONE
st.markdown("""
    <div style='text-align: center; padding: 10px; border-bottom: 2px solid #f0f2f6;'>
        <h1 style='color: #1E3A8A; margin-bottom: 0;'>☀️ AJC SOLUÇÕES EM ENERGIA</h1>
        <p style='color: #6B7280; font-size: 1.1em;'>Simulador de Geração Fotovoltaica e Viabilidade Financeira</p>
    </div>
    """, unsafe_allow_html=True)

if not df_rs.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. ENTRADA DE DADOS
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📍 Localização")
        lista_cidades = sorted(df_rs['cidade'].unique())
        cidade_selecionada = st.selectbox("Selecione o Município do RS:", lista_cidades)
        
        dados_cidade = df_rs[df_rs['cidade'] == cidade_selecionada].iloc[0]
        
        st.info(f"**Concessionária:** {dados_cidade['concessionaria']} | **HSP:** {dados_cidade['hsp']}")
        tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

    with c2:
        st.subheader("⚙️ Dimensionamento")
        cc1, cc2 = st.columns(2)
        p_painel = cc1.number_input("Potência do Painel (Wp)", value=550)
        qtd_painel = cc2.number_input("Quantidade de Painéis", value=10)
        
        potencia_total_kwp = (p_painel * qtd_painel) / 1000
        st.success(f"**Capacidade Instalada:** {potencia_total_kwp:.2f} kWp")
        pr = st.slider("Eficiência Estimada (PR)", 0.70, 0.90, 0.80)

    # 5. CÁLCULOS E DEFINIÇÃO DA ORDEM CRONOLÓGICA
    # Lista mestra para ordem cronológica
    meses_ordem = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    fatores_sazonalidade = [1.28, 1.12, 1.05, 0.82, 0.65, 0.58, 0.62, 0.75, 0.88, 1.02, 1.15, 1.25]
    
    hsp_anual = dados_cidade['hsp']
    geracao_base = potencia_total_kwp * hsp_anual * pr * 30.4
    
    # Gerando os dados mensais seguindo a ordem da lista meses_ordem
    geracao_mensal = [round(geracao_base * f, 2) for f in fatores_sazonalidade]
    
    # Cálculo Econômico GD2 (2026)
    fio_b_perc = dados_cidade['fio_b']
    custo_fio_b = (tarifa * fio_b_perc) * 0.60
    tarifa_liquida = tarifa - custo_fio_b
    economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal]

    # 6. EXIBIÇÃO DE RESULTADOS (METRICS)
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Geração Média Mensal", f"{np.mean(geracao_mensal):.2f} kWh")
    r2.metric("Economia Anual Estimada", f"R$ {sum(economia_mensal):.2f}")
    r3.metric("Valor do Crédito Líquido", f"R$ {tarifa_liquida:.2f}")

    # 7. GRÁFICO CORRIGIDO PARA ORDEM CRONOLÓGICA
    st.markdown("### 📈 Curva de Geração Mensal")
    
    # Criamos o DataFrame
    df_grafico = pd.DataFrame({
        "Mês": meses_ordem,
        "Geração (kWh)": geracao_mensal
    })
    
    # CONVERSÃO CRÍTICA: Definir a coluna 'Mês' como categoria ordenada para evitar ordem alfabética
    df_grafico['Mês'] = pd.Categorical(df_grafico['Mês'], categories=meses_ordem, ordered=True)
    
    # Ao usar o .set_index("Mês"), o Streamlit respeitará a ordem categórica definida acima
    st.bar_chart(df_grafico.set_index("Mês"))

    # 8. DETALHAMENTO EM TABELA
    with st.expander("Ver tabela detalhada de geração e economia"):
        df_detalhe = pd.DataFrame({
            "Mês": meses_ordem,
            "Geração (kWh)": geracao_mensal,
            "Economia (R$)": economia_mensal
        })
        st.table(df_detalhe)

    st.divider()
    st.caption(f"☀️ AJC Soluções em Energia | Local: {cidade_selecionada} | Regra: GD2 (Lei 14.300)")

else:
    st.error("Erro: O arquivo 'cidades_rs_completo.csv' não foi encontrado no repositório.")
