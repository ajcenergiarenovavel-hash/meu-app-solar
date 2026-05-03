import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# 2. FUNÇÃO PARA CARREGAR DADOS CORRIGIDA
@st.cache_data
def carregar_dados():
    try:
        # Agora configurado para o padrão internacional (vírgula e ponto)
        df = pd.read_csv('cidades_rs_completo.csv', sep=',', decimal='.')
        
        # Limpeza extra: garante que não haja espaços nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # Converte colunas críticas para numérico (evita erros de leitura do CSV)
        cols_numericas = ['lat', 'lon', 'hsp', 'fio_b']
        for col in cols_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except FileNotFoundError:
        st.error("Erro: O arquivo 'cidades_rs_completo.csv' não foi encontrado no GitHub.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na leitura dos dados: {e}")
        return pd.DataFrame()

df_rs = carregar_dados()

# 3. CABEÇALHO
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
        # Ordena a lista de cidades para facilitar a busca
        lista_cidades = sorted(df_rs['cidade'].unique())
        cidade_selecionada = st.selectbox("Município do RS:", lista_cidades)
        
        # Busca a linha correspondente à cidade
        dados_cidade = df_rs[df_rs['cidade'] == cidade_selecionada].iloc[0]
        
        st.info(f"**Dados Técnicos:** {dados_cidade['concessionaria']} | HSP: {dados_cidade['hsp']}")
        tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

    with c2:
        st.subheader("⚙️ Sistema")
        cc1, cc2 = st.columns(2)
        p_painel = cc1.number_input("Painel (Wp)", value=550)
        qtd_painel = cc2.number_input("Quantidade", value=10)
        potencia_total_kwp = (p_painel * qtd_painel) / 1000
        pr = st.slider("Eficiência (PR)", 0.70, 0.90, 0.80)

    # 5. CÁLCULOS
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    fatores_mensais = [1.28, 1.12, 1.05, 0.82, 0.65, 0.58, 0.62, 0.75, 0.88, 1.02, 1.15, 1.25]
    
    hsp_local = dados_cidade['hsp']
    # Cálculo: Potência * HSP * Eficiência * Dias do Mês
    geracao_base = potencia_total_kwp * hsp_local * pr * 30.4
    
    geracao_mensal_kwh = [round(geracao_base * f, 2) for f in fatores_mensais]
    
    # Regra GD2: 60% do Fio B pago pelo cliente
    encargo_fio_b = (tarifa * dados_cidade['fio_b']) * 0.60
    tarifa_liquida = tarifa - encargo_fio_b
    economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal_kwh]

    # 6. EXIBIÇÃO
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Geração Média Mensal", f"{np.mean(geracao_mensal_kwh):.2f} kWh")
    r2.metric("Economia Anual Estimada", f"R$ {sum(economia_mensal):.2f}")
    r3.metric("Crédito Líquido", f"R$ {tarifa_liquida:.2f}/kWh")

    # 7. GRÁFICO
    st.markdown("### 📈 Geração Estimada Mês a Mês")
    df_grafico = pd.DataFrame({"Mês": meses, "kWh": geracao_mensal_kwh})
    st.bar_chart(df_grafico.set_index("Mês"))

    st.caption(f"Dados baseados nas coordenadas: {dados_cidade['lat']}, {dados_cidade['lon']}")

else:
    st.warning("Aguardando carregamento do arquivo CSV...")
