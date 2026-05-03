import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Simulador Solar AJC", 
    layout="wide", 
    page_icon="☀️"
)

# 2. FUNÇÃO PARA CARREGAR DADOS (Otimizada para o novo CSV)
@st.cache_data
def carregar_dados():
    try:
        # Lê o arquivo considerando separador de vírgula e ponto decimal
        df = pd.read_csv('cidades_rs_completo.csv', sep=',', decimal='.')
        
        # Limpa eventuais espaços em branco nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # Garante que as colunas críticas sejam numéricas
        cols_numericas = ['lat', 'lon', 'hsp', 'fio_b']
        for col in cols_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except FileNotFoundError:
        st.error("Erro: O arquivo 'cidades_rs_completo.csv' não foi encontrado no GitHub.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
        return pd.DataFrame()

df_rs = carregar_dados()

# 3. CABEÇALHO PERSONALIZADO AJC
st.markdown("""
    <div style='text-align: center; padding: 15px; border-bottom: 2px solid #f0f2f6;'>
        <h1 style='color: #1E3A8A; margin-bottom: 0;'>AJC SOLUÇÕES EM ENERGIA</h1>
        <p style='color: #6B7280; font-size: 1.1em;'>Simulador Técnico de Geração Fotovoltaica</p>
    </div>
    """, unsafe_allow_html=True)

if not df_rs.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. ENTRADA DE DADOS
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📍 Localização do Projeto")
        # Lista de cidades em ordem alfabética
        lista_cidades = sorted(df_rs['cidade'].unique())
        cidade_sel = st.selectbox("Selecione o Município do RS:", lista_cidades)
        
        # Filtra os dados da cidade escolhida
        dados = df_rs[df_rs['cidade'] == cidade_sel].iloc[0]
        
        # Exibe informações técnicas da base
        st.info(f"**Concessionária:** {dados['concessionaria']} | **HSP Médio:** {dados['hsp']} kWh/m².dia")
        tarifa = st.number_input("Tarifa da Concessionária (R$/kWh)", value=1.02, step=0.01)

    with c2:
        st.subheader("⚙️ Dados do Sistema")
        col_p, col_q = st.columns(2)
        p_painel = col_p.number_input("Potência do Painel (Wp)", value=550)
        qtd_painel = col_q.number_input("Quantidade de Placas", value=10)
        
        potencia_total_kwp = (p_painel * qtd_painel) / 1000
        st.metric("Capacidade Total", f"{potencia_total_kwp:.2f} kWp")
        
        pr = st.slider("Eficiência Estimada (Performance Ratio)", 0.70, 0.90, 0.80)

    # 5. CÁLCULOS TÉCNICOS (Sazonalidade RS e Regras GD2)
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    # Fatores típicos de irradiação mensal para o RS
    fatores_mensais = [1.28, 1.12, 1.05, 0.82, 0.65, 0.58, 0.62, 0.75, 0.88, 1.02, 1.15, 1.25]
    
    # Cálculo de geração baseado no HSP do novo arquivo
    geracao_base = potencia_total_kwp * dados['hsp'] * pr * 30.4
    geracao_mensal = [round(geracao_base * f, 2) for f in fatores_mensais]
    
    # Regra GD2 (2026): Pagamento de 60% do encargo do Fio B
    encargo_fio_b = (tarifa * dados['fio_b']) * 0.60
    tarifa_liquida = tarifa - encargo_fio_b
    economia_mensal = [round(g * tarifa_liquida, 2) for g in geracao_mensal]

    # 6. EXIBIÇÃO DE RESULTADOS
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("Geração Média Mensal", f"{np.mean(geracao_mensal):.2f} kWh")
    r2.metric("Economia Anual Estimada", f"R$ {sum(economia_mensal):.2f}")
    r3.metric("Crédito Líquido", f"R$ {tarifa_liquida:.2f}/kWh")

    # 7. GRÁFICO DE GERAÇÃO (Ordenado de Jan a Dez)
    st.markdown("### 📈 Estimativa de Geração Mensal (kWh)")
    df_grafico = pd.DataFrame({"Mês": meses, "Geração (kWh)": geracao_mensal})
    st.bar_chart(df_grafico.set_index("Mês"))

    # 8. RODAPÉ TÉCNICO
    st.markdown("---")
    st.caption(f"Simulador AJC Soluções em Energia | Coordenadas: {dados['lat']}, {dados['lon']} | Base de Dados: cidades_rs_completo.csv")

else:
    st.warning("Aguardando o upload do arquivo 'cidades_rs_completo.csv' no GitHub.")
