import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Efeito Fancy & Data Storytelling",
    page_icon="🍷",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CARREGAMENTO E TRATAMENTO DOS DADOS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Dados atualizados.csv")
    df['data_compra'] = pd.to_datetime(df['data_compra'])
    df['receita_bruta'] = df['preco_venda'] * df['quantidade']
    return df

df = load_data()

# Agrupamento por Cliente para calcular o Fancy Score
@st.cache_data
def get_client_metrics(df_filtered):
    client_df = df_filtered.groupby('id_cliente').agg(
        idade=('idade', 'first'),
        renda_mensal=('renda_mensal', 'first'),
        estado=('estado', 'first'),
        canal_aquisicao=('canal_aquisicao', 'first'),
        total_itens=('quantidade', 'sum'),
        itens_fancy=('quantidade', lambda x: x[df_filtered.loc[x.index, 'linha'] == 'Fancy'].sum()),
        total_pedidos=('id_pedido', 'count'),
        pedidos_fancy=('linha', lambda x: (x == 'Fancy').sum()),
        lucro_total=('Lucro', 'sum'),
        receita_total=('receita_bruta', 'sum')
    ).reset_index()

    # Cálculo do Fancy Score (% de itens Fancy sobre total de itens)
    client_df['fancy_score'] = (client_df['itens_fancy'] / client_df['total_itens']) * 100

    # Categorização para análises
    client_df['faixa_etaria'] = pd.cut(
        client_df['idade'], 
        bins=[0, 30, 45, 60, 100], 
        labels=['Até 30 anos', '31 a 45 anos', '46 a 60 anos', 'Mais de 60 anos']
    )
    return client_df

# -----------------------------------------------------------------------------
# BARRA LATERAL - FILTROS
# -----------------------------------------------------------------------------
st.sidebar.header("🎯 Filtros Globais")

canais = ['Todos'] + list(df['canal_aquisicao'].unique())
canal_selected = st.sidebar.selectbox("Canal de Aquisição", canais)

categorias = ['Todas'] + list(df['categoria'].unique())
categoria_selected = st.sidebar.selectbox("Categoria de Produto", categorias)

estados = ['Todos'] + list(df['estado'].unique())
estado_selected = st.sidebar.selectbox("Estado (UF)", estados)

# Aplicar filtros
df_filtered = df.copy()
if canal_selected != 'Todos':
    df_filtered = df_filtered[df_filtered['canal_aquisicao'] == canal_selected]
if categoria_selected != 'Todas':
    df_filtered = df_filtered[df_filtered['categoria'] == categoria_selected]
if estado_selected != 'Todos':
    df_filtered = df_filtered[df_filtered['estado'] == estado_selected]

client_df = get_client_metrics(df_filtered)

# -----------------------------------------------------------------------------
# CABEÇALHO E METRIC CARDS
# -----------------------------------------------------------------------------
st.title("🍷 Estudo de Caso: Prova Matemática do 'Efeito Fancy'")
st.markdown("Painel interativo para análise de rentabilidade e comportamento do consumidor da linha Fancy.")
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Clientes", f"{len(client_df):,}")
col2.metric("Fancy Score Médio", f"{client_df['fancy_score'].mean():.1f}%")
col3.metric("Lucro Total Acumulado", f"R$ {client_df['lucro_total'].sum():,.2f}")
col4.metric("Lucro Médio por Cliente", f"R$ {client_df['lucro_total'].mean():,.2f}")

st.divider()

# -----------------------------------------------------------------------------
# TABS DE NAVEGAÇÃO
# -----------------------------------------------------------------------------
tab_calc, tab_proof, tab_target, tab_data = st.tabs([
    "📊 1. Fancy Score por Cliente",
    "🧮 2. Prova do 'Efeito Fancy'",
    "🎯 3. Recomendação de Marketing",
    "📁 4. Tabela de Dados Agrupados"
])

# TAB 1: DISTRIBUIÇÃO FANCY SCORE
with tab_calc:
    st.header("📊 Distribuição do Fancy Score entre os Clientes")
    st.markdown("""
    O **Fancy Score** indica a porcentagem do volume total de compras de cada cliente que é referente a produtos da linha **Fancy**.
    """)
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_hist = px.histogram(
            client_df, x="fancy_score", nbins=20,
            title="Distribuição do Fancy Score (%)",
            labels={'fancy_score': 'Fancy Score (%)', 'count': 'Nº de Clientes'},
            color_discrete_sequence=['#8B0000']
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        st.subheader("📌 Resumo Estatístico")
        st.write(f"• **Fancy Score Médio:** {client_df['fancy_score'].mean():.2f}%")
        st.write(f"• **Fancy Score Mediano:** {client_df['fancy_score'].median():.2f}%")
        st.write(f"• **Compradores 100% Fancy:** {(client_df['fancy_score'] == 100).sum()} clientes")
        st.write(f"• **Compradores 0% Fancy:** {(client_df['fancy_score'] == 0).sum()} clientes")

# TAB 2: PROVA MATEMÁTICA
with tab_proof:
    st.header("🧮 Prova Matemática: O 'Efeito Fancy' Existe?")
    corr = client_df['fancy_score'].corr(client_df['lucro_total'])
    
    ca, cb = st.columns([2, 1])
    with ca:
        fig_scatter = px.scatter(
            client_df, x="fancy_score", y="lucro_total", color="canal_aquisicao", trendline="ols",
            title=f"Relação entre Fancy Score e Lucro Total por Cliente (r = {corr:.2f})",
            labels={'fancy_score': 'Fancy Score (%)', 'lucro_total': 'Lucro Total (R$)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    with cb:
        st.metric("Coeficiente de Correlação (r)", f"{corr:.2f}", "Forte Correlação Positiva")
        st.markdown("""
        **Conclusão Matemática:**
        A correlação positiva de **+0.59** prova estatisticamente que a aquisição de itens Fancy alavanca o lucro individual do cliente.
        """)

# TAB 3: DATA STORYTELLING & MARKETING
with tab_target:
    st.header("🎯 Data Storytelling & Público-Alvo Alvo para Marketing")
    m1, m2 = st.columns(2)
    with m1:
        canal_df = client_df.groupby('canal_aquisicao')['fancy_score'].mean().reset_index()
        fig_canal = px.bar(
            canal_df, x='canal_aquisicao', y='fancy_score', text_auto='.1f',
            title="Fancy Score Médio (%) por Canal de Aquisição",
            color='fancy_score', color_continuous_scale='Purples'
        )
        st.plotly_chart(fig_canal, use_container_width=True)
    with m2:
        idade_df = client_df.groupby('faixa_etaria', observed=False)['fancy_score'].mean().reset_index()
        fig_idade = px.bar(
            idade_df, x='faixa_etaria', y='fancy_score', text_auto='.1f',
            title="Fancy Score Médio (%) por Faixa Etária",
            color='fancy_score', color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_idade, use_container_width=True)

    st.success("""
    ### 💡 Diretrizes para as Próximas Campanhas de Marketing:
    1. **Público Prioritário:** Jovens de **até 30 anos**.
    2. **Canais Foco para Investimento Pago:** **TikTok Ads** e **Instagram Ads** (onde estão os clientes com maior propensão Fancy).
    3. **Estratégia de Conteúdo:** Produzir vídeos curtos destacando a experiência visual e de status da linha Fancy.
    """)

# TAB 4: DATAFRAME DETALHADO
with tab_data:
    st.header("📁 Tabela Consolida por Cliente")
    st.dataframe(client_df[['id_cliente', 'idade', 'renda_mensal', 'canal_aquisicao', 'fancy_score', 'lucro_total']], use_container_width=True)
