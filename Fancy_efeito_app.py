import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

st.set_page_config(
    page_title="Efeito Fancy",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Análise do Efeito Fancy")

st.markdown(
    "Dashboard para análise do comportamento de compra de produtos "
    "da linha Fancy e identificação do público-alvo."
)

# --------------------------------------------------
# CARREGAMENTO DOS DADOS
# --------------------------------------------------

@st.cache_data
def carregar_dados():

    arquivo = Path(__file__).parent / "Dados atualizados.csv"

    if not arquivo.exists():
        st.error(
            "❌ O arquivo 'Dados atualizados.csv' não foi encontrado. "
            "Verifique se ele está no GitHub."
        )
        st.stop()

    try:
        df = pd.read_csv(
            arquivo,
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            arquivo,
            encoding="latin1"
        )

    except pd.errors.EmptyDataError:
        st.error(
            "❌ O arquivo CSV está vazio."
        )
        st.stop()

    if df.empty:
        st.error(
            "❌ O CSV foi carregado, mas não possui registros."
        )
        st.stop()

    return df


df = carregar_dados()

# --------------------------------------------------
# VERIFICAÇÃO DAS COLUNAS
# --------------------------------------------------

colunas_necessarias = [
    "id_cliente",
    "id_pedido",
    "linha",
    "preco_venda",
    "quantidade",
    "idade",
    "renda_mensal",
    "estado",
    "canal_aquisicao"
]

colunas_faltantes = [
    coluna
    for coluna in colunas_necessarias
    if coluna not in df.columns
]

if colunas_faltantes:

    st.error(
        "❌ As seguintes colunas não foram encontradas no CSV:"
    )

    st.write(colunas_faltantes)

    st.stop()

# --------------------------------------------------
# TRATAMENTO DOS DADOS
# --------------------------------------------------

df["preco_venda"] = pd.to_numeric(
    df["preco_venda"],
    errors="coerce"
)

df["quantidade"] = pd.to_numeric(
    df["quantidade"],
    errors="coerce"
)

df["idade"] = pd.to_numeric(
    df["idade"],
    errors="coerce"
)

df["renda_mensal"] = pd.to_numeric(
    df["renda_mensal"],
    errors="coerce"
)

# Remove registros sem dados essenciais
df = df.dropna(
    subset=[
        "id_cliente",
        "id_pedido",
        "preco_venda",
        "quantidade"
    ]
)

# --------------------------------------------------
# RECEITA
# --------------------------------------------------

df["receita"] = (
    df["preco_venda"] *
    df["quantidade"]
)

# --------------------------------------------------
# FANCY SCORE POR CLIENTE
# --------------------------------------------------

cliente = df.groupby("id_cliente").agg(

    total_compras=(
        "id_pedido",
        "count"
    ),

    compras_fancy=(
        "linha",
        lambda x: (x == "Fancy").sum()
    ),

    quantidade_total=(
        "quantidade",
        "sum"
    ),

    receita=(
        "receita",
        "sum"
    ),

    idade=(
        "idade",
        "first"
    ),

    renda_mensal=(
        "renda_mensal",
        "first"
    ),

    estado=(
        "estado",
        "first"
    ),

    canal_aquisicao=(
        "canal_aquisicao",
        "first"
    )

).reset_index()

# --------------------------------------------------
# FANCY SCORE
# --------------------------------------------------

cliente["fancy_score"] = np.where(
    cliente["total_compras"] > 0,
    (
        cliente["compras_fancy"] /
        cliente["total_compras"]
    ) * 100,
    0
)

# --------------------------------------------------
# TICKET MÉDIO
# --------------------------------------------------

cliente["ticket_medio"] = np.where(
    cliente["total_compras"] > 0,
    cliente["receita"] /
    cliente["total_compras"],
    0
)

# --------------------------------------------------
# KPIs
# --------------------------------------------------

total_clientes = (
    cliente["id_cliente"].nunique()
)

fancy_score_medio = (
    cliente["fancy_score"].mean()
)

ticket_medio = (
    cliente["ticket_medio"].mean()
)

participacao_fancy = (
    (df["linha"] == "Fancy").mean()
) * 100

# --------------------------------------------------
# CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Clientes",
    f"{total_clientes:,}".replace(",", ".")
)

col2.metric(
    "Fancy Score médio",
    f"{fancy_score_medio:.1f}%"
)

col3.metric(
    "Ticket médio",
    (
        f"R$ {ticket_medio:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
)

col4.metric(
    "Compras Fancy",
    f"{participacao_fancy:.1f}%"
)

st.divider()

# --------------------------------------------------
# 1. DISTRIBUIÇÃO DO FANCY SCORE
# --------------------------------------------------

st.subheader(
    "1. Distribuição do Fancy Score"
)

fig_score = px.histogram(
    cliente,
    x="fancy_score",
    nbins=20,
    title="Distribuição do Fancy Score por cliente",
    labels={
        "fancy_score": "Fancy Score (%)",
        "count": "Quantidade de clientes"
    }
)

fig_score.update_layout(
    xaxis_title="Fancy Score (%)",
    yaxis_title="Clientes"
)

st.plotly_chart(
    fig_score,
    use_container_width=True
)

# --------------------------------------------------
# 2. CORRELAÇÃO FANCY SCORE X TICKET
# --------------------------------------------------

st.subheader(
    "2. Fancy Score × Ticket Médio"
)

dados_correlacao = cliente[
    [
        "fancy_score",
        "ticket_medio"
    ]
].dropna()

if len(dados_correlacao) > 1:

    correlacao = (
        dados_correlacao
        .corr()
        .iloc[0, 1]
    )

else:

    correlacao = np.nan

fig_scatter = px.scatter(
    cliente,
    x="fancy_score",
    y="ticket_medio",
    opacity=0.5,
    title="Relação entre Fancy Score e Ticket Médio",
    labels={
        "fancy_score": "Fancy Score (%)",
        "ticket_medio": "Ticket Médio (R$)"
    }
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

if pd.notna(correlacao):

    st.info(
        f"Correlação entre Fancy Score e Ticket Médio: "
        f"{correlacao:.3f}"
    )

else:

    st.warning(
        "Não foi possível calcular a correlação."
    )

# --------------------------------------------------
# 3. TESTE DO EFEITO FANCY
# --------------------------------------------------

st.subheader(
    "3. Evidência matemática do Efeito Fancy"
)

cliente["grupo_fancy"] = np.where(
    cliente["fancy_score"] >= 50,
    "Fancy Score ≥ 50%",
    "Fancy Score < 50%"
)

grupo_fancy = cliente[
    cliente["grupo_fancy"] == "Fancy Score ≥ 50%"
]

grupo_padrao = cliente[
    cliente["grupo_fancy"] == "Fancy Score < 50%"
]

ticket_fancy = (
    grupo_fancy["ticket_medio"].mean()
    if not grupo_fancy.empty
    else np.nan
)

ticket_padrao = (
    grupo_padrao["ticket_medio"].mean()
    if not grupo_padrao.empty
    else np.nan
)

# --------------------------------------------------
# DIFERENÇA
# --------------------------------------------------

if (
    pd.notna(ticket_fancy)
    and
    pd.notna(ticket_padrao)
    and
    ticket_padrao != 0
):

    diferenca_ticket = (
        (
            ticket_fancy /
            ticket_padrao
        ) - 1
    ) * 100

else:

    diferenca_ticket = np.nan

# --------------------------------------------------
# CARDS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Ticket — Fancy ≥ 50%",
    (
        f"R$ {ticket_fancy:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
        if pd.notna(ticket_fancy)
        else "N/A"
    )
)

col2.metric(
    "Ticket — Fancy < 50%",
    (
        f"R$ {ticket_padrao:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
        if pd.notna(ticket_padrao)
        else "N/A"
    )
)

col3.metric(
    "Diferença",
    (
        f"{diferenca_ticket:+.1f}%"
        if pd.notna(diferenca_ticket)
        else "N/A"
    )
)

# --------------------------------------------------
# COMPARAÇÃO
# --------------------------------------------------

comparacao = pd.DataFrame({

    "Grupo": [
        "Fancy Score ≥ 50%",
        "Fancy Score < 50%"
    ],

    "Ticket Médio": [
        ticket_fancy,
        ticket_padrao
    ]

})

fig_comparacao = px.bar(
    comparacao,
    x="Grupo",
    y="Ticket Médio",
    text_auto=".2f",
    title="Comparação do Ticket Médio"
)

st.plotly_chart(
    fig_comparacao,
    use_container_width=True
)

if pd.notna(diferenca_ticket):

    if diferenca_ticket >= 0:

        st.success(
            f"Clientes com Fancy Score ≥ 50% apresentam "
            f"ticket médio {diferenca_ticket:.1f}% maior "
            f"que os demais clientes."
        )

    else:

        st.warning(
            f"Clientes com Fancy Score ≥ 50% apresentam "
            f"ticket médio {abs(diferenca_ticket):.1f}% menor "
            f"que os demais clientes."
        )

# --------------------------------------------------
# 4. PÚBLICO-ALVO
# --------------------------------------------------

st.subheader(
    "4. Público-alvo recomendado para Marketing"
)

cliente["faixa_etaria"] = pd.cut(

    cliente["idade"],

    bins=[
        17,
        24,
        34,
        44,
        54,
        69,
        np.inf
    ],

    labels=[
        "18–24",
        "25–34",
        "35–44",
        "45–54",
        "55–69",
        "70+"
    ],

    include_lowest=True
)

segmento = cliente.groupby(
    [
        "canal_aquisicao",
        "faixa_etaria"
    ],
    observed=True
).agg(

    clientes=(
        "id_cliente",
        "count"
    ),

    fancy_score=(
        "fancy_score",
        "mean"
    ),

    ticket_medio=(
        "ticket_medio",
        "mean"
    )

).reset_index()

segmento = segmento.sort_values(
    "fancy_score",
    ascending=False
)

# --------------------------------------------------
# GRÁFICO
# --------------------------------------------------

fig_segmento = px.bar(

    segmento.head(10),

    x="fancy_score",

    y="canal_aquisicao",

    color="faixa_etaria",

    orientation="h",

    title="Top 10 segmentos por Fancy Score",

    labels={

        "fancy_score":
        "Fancy Score médio (%)",

        "canal_aquisicao":
        "Canal",

        "faixa_etaria":
        "Faixa etária"

    }
)

st.plotly_chart(
    fig_segmento,
    use_container_width=True
)

# --------------------------------------------------
# RECOMENDAÇÃO DE MARKETING
# --------------------------------------------------

st.markdown(
    "### 🎯 Recomendação de Marketing"
)

if not segmento.empty:

    principal = segmento.iloc[0]

    st.write(
        f"""
        O segmento com maior Fancy Score médio é composto por
        consumidores da faixa etária **{principal['faixa_etaria']}**,
        no canal **{principal['canal_aquisicao']}**.

        Esse segmento apresenta Fancy Score médio de
        **{principal['fancy_score']:.1f}%** e ticket médio de
        **R$ {principal['ticket_medio']:,.2f}**.

        Esses dados podem ser utilizados como referência para
        direcionar campanhas de marketing e estratégias de comunicação.
        """
    )

else:

    st.warning(
        "Não existem dados suficientes para gerar uma recomendação."
    )

# --------------------------------------------------
# 5. TABELA DE SEGMENTOS
# --------------------------------------------------

st.subheader(
    "5. Ranking de segmentos"
)

st.dataframe(
    segmento,
    use_container_width=True
)
