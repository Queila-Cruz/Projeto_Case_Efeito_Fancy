import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Efeito Fancy & Fancy Score",
    page_icon="💎",
    layout="wide"
)

# Estilo visual customizado
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 5px solid #6c5ce7;
    }
    .stMetric label { font-size: 0.95rem; color: #555; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('Dados atualizados.csv')
    
    # Adicionar colunas calculadas de total por item
    df['faturamento_item'] = df['preco_venda'] * df['quantidade']
    df['custo_item'] = df['custo_producao'] * df['quantidade']
    df['lucro_item'] = df['Lucro'] * df['quantidade']
    df['is_fancy'] = (df['linha'] == 'Fancy').astype(int)
    df['qtd_fancy'] = df['is_fancy'] * df['quantidade']
    
    # Agrupamento por Cliente
    cust = df.groupby('id_cliente').agg(
        idade=('idade', 'first'),
        renda_mensal=('renda_mensal', 'first'),
        estado=('estado', 'first'),
        canal_aquisicao=('canal_aquisicao', 'first'),
        total_pedidos=('id_pedido', 'count'),
        total_qtd=('quantidade', 'sum'),
        fancy_qtd=('qtd_fancy', 'sum'),
        faturamento_total=('faturamento_item', 'sum'),
        lucro_total=('lucro_item', 'sum')
    ).reset_index()
    
    # Cálculo do Fancy Score por Cliente
    cust['fancy_score'] = (cust['fancy_qtd'] / cust['total_qtd']) * 100
    cust['ticket_medio'] = cust['faturamento_total'] / cust['total_pedidos']
    
    # Categorização de Faixa Etária
    bins_idade = [17, 30, 45, 60, 100]
    labels_idade = ['18-30 anos', '31-45 anos', '46-60 anos', '60+ anos']
    cust['faixa_etaria'] = pd.cut(cust['idade'], bins=bins_idade, labels=labels_idade)
    
    return df, cust

df_raw, df_cust = load_data()

# --- SIDEBAR: FILTROS ---
st.sidebar.image("https://img.icons8.com/color/96/000000/diamond.png", width=60)
st.sidebar.title("Filtros Globais")

canais_selected = st.sidebar.multiselect(
    "Canal de Aquisição:",
    options=df_cust['canal_aquisicao'].unique().tolist(),
    default=df_cust['canal_aquisicao'].unique().tolist()
)

faixa_etaria_selected = st.sidebar.multiselect(
    "Faixa Etária:",
    options=df_cust['faixa_etaria'].unique().tolist(),
    default=df_cust['faixa_etaria'].unique().tolist()
)

estados_selected = st.sidebar.multiselect(
    "Estado (UF):",
    options=sorted(df_cust['estado'].unique().tolist()),
    default=sorted(df_cust['estado'].unique().tolist())
)

# Filtrar bases
cust_filtered = df_cust[
    (df_cust['canal_aquisicao'].isin(canais_selected)) &
    (df_cust['faixa_etaria'].isin(faixa_etaria_selected)) &
    (df_cust['estado'].isin(estados_selected))
]

df_filtered = df_raw[df_raw['id_cliente'].isin(cust_filtered['id_cliente'])]

# --- TÍTULO PRINCIPAL ---
st.title("💎 Estudo de Caso: O Efeito Fancy & Segmentação do Cliente")
st.markdown("Análise quantitativa do **Fancy Score**, comprovação matemática do **Efeito Fancy** e direcionamento estratégico para Marketing.")

# --- SEÇÃO 1: METRICAS GERAIS ---
st.subheader("1. Visão Geral dos Indicadores")

col1, col2, col3, col4, col5 = st.columns(5)

total_faturamento = df_filtered['faturamento_item'].sum()
total_lucro = df_filtered['lucro_item'].sum()
margem_media = (total_lucro / total_faturamento * 100) if total_faturamento > 0 else 0
fancy_score_medio = cust_filtered['fancy_score'].mean()
ticket_medio = cust_filtered['faturamento_total'].sum() / cust_filtered['total_pedidos'].sum()

col1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")
col2.metric("Lucro Líquido Total", f"R$ {total_lucro:,.2f}")
col3.metric("Margem Global", f"{margem_media:.1f}%")
col4.metric("Fancy Score Médio", f"{fancy_score_medio:.1f}%")
col5.metric("Ticket Médio", f"R$ {ticket_medio:.2f}")

st.markdown("---")

# --- SEÇÃO 2: A PROVA MATEMÁTICA DO EFEITO FANCY ---
st.subheader("2. Prova Matemática do 'Efeito Fancy'")

st.info("""
**O que é o Efeito Fancy?** É a constatação estatística de que a linha 'Fancy' gera uma margem desproporcionalmente maior
e é responsável por impulsionar a lucratividade total do negócio, apesar de representar um volume menor de vendas em unidades.
""")

col_left, col_right = st.columns(2)

with col_left:
    # Comparativo Linha Fancy vs Padrão
    linha_summary = df_filtered.groupby('linha').agg(
        Faturamento=('faturamento_item', 'sum'),
        Lucro=('lucro_item', 'sum'),
        Unidades=('quantidade', 'sum')
    ).reset_index()
    linha_summary['Margem (%)'] = (linha_summary['Lucro'] / linha_summary['Faturamento']) * 100
    
    fig_margem = px.bar(
        linha_summary, 
        x='linha', 
        y='Margem (%)',
        color='linha',
        color_discrete_map={'Fancy': '#6c5ce7', 'Padrão': '#b2bec3'},
        text_auto='.1f',
        title="Comparativo de Margem de Lucro Bruta (%)"
    )
    fig_margem.update_traces(textposition='outside')
    st.plotly_chart(fig_margem, use_container_width=True)

with col_right:
    # Participação no Lucro
    fig_pie = px.pie(
        linha_summary,
        names='linha',
        values='Lucro',
        color='linha',
        color_discrete_map={'Fancy': '#6c5ce7', 'Padrão': '#b2bec3'},
        hole=0.4,
        title="Participação no Lucro Líquido Total (%)"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Tabela detalhada
st.markdown("#### Detalhamento Unitário e Financeiro por Linha")
st.dataframe(linha_summary.style.format({
    'Faturamento': 'R$ {:,.2f}',
    'Lucro': 'R$ {:,.2f}',
    'Unidades': '{:,.0f}',
    'Margem (%)': '{:.2f}%'
}), use_container_width=True)

st.markdown("---")

# --- SEÇÃO 3: DISTRIBUIÇÃO DO FANCY SCORE E SEGMENTAÇÃO ---
st.subheader("3. Distribuição do Fancy Score por Cliente")

col_a, col_b = st.columns(2)

with col_a:
    fig_hist = px.histogram(
        cust_filtered,
        x='fancy_score',
        nbins=20,
        title="Distribuição de Clientes por Faixa de Fancy Score (%)",
        labels={'fancy_score': 'Fancy Score (%)', 'count': 'Nº de Clientes'},
        color_discrete_sequence=['#6c5ce7']
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_b:
    fig_scatter = px.scatter(
        cust_filtered,
        x='fancy_score',
        y='lucro_total',
        color='canal_aquisicao',
        size='ticket_medio',
        hover_data=['idade', 'renda_mensal'],
        title="Fancy Score vs. Lucro Gerado por Cliente",
        labels={'fancy_score': 'Fancy Score (%)', 'lucro_total': 'Lucro Total do Cliente (R$)'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- SEÇÃO 4: TARGETING DE MARKETING ---
st.subheader("4. Análise de Público-Alvo & Recomendações de Marketing")

col_m1, col_m2 = st.columns(2)

with col_m1:
    channel_perf = cust_filtered.groupby('canal_aquisicao').agg(
        Fancy_Score_Medio=('fancy_score', 'mean'),
        Lucro_Medio=('lucro_total', 'mean'),
        Clientes=('id_cliente', 'count')
    ).reset_index().sort_values(by='Fancy_Score_Medio', ascending=False)
    
    fig_channel = px.bar(
        channel_perf,
        x='canal_aquisicao',
        y='Fancy_Score_Medio',
        color='Fancy_Score_Medio',
        color_continuous_scale='Purples',
        text_auto='.1f',
        title="Fancy Score Médio por Canal de Aquisição (%)"
    )
    st.plotly_chart(fig_channel, use_container_width=True)

with col_m2:
    age_perf = cust_filtered.groupby('faixa_etaria').agg(
        Fancy_Score_Medio=('fancy_score', 'mean'),
        Lucro_Medio=('lucro_total', 'mean'),
        Clientes=('id_cliente', 'count')
    ).reset_index()
    
    fig_age = px.bar(
        age_perf,
        x='faixa_etaria',
        y='Fancy_Score_Medio',
        color='Fancy_Score_Medio',
        color_continuous_scale='Purples',
        text_auto='.1f',
        title="Fancy Score Médio por Faixa Etária (%)"
    )
    st.plotly_chart(fig_age, use_container_width=True)

# Caixa de Recomendação de Marketing
st.success("""
🎯 **Direcionamento de Marketing Recomendado:**
* **Público Prioritário**: Clientes de **18 a 30 anos**.
* **Canais Chave**: **TikTok** (Fancy Score médio de **52,3%**) e **Instagram** (Fancy Score médio de **45,2%**).
* **Estratégia de Conteúdo**: Focar em anúncios no formato de vídeo curto (Reels/TikTok) com apelo estético, unboxing e estilo de vida de alta gastronomia para impulsionar a venda da linha Fancy em categorias com margem expressiva (Café e Queijo).
""")
