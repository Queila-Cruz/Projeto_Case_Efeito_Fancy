import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Efeito Fancy | Data Storytelling",
    page_icon="✨",
    layout="wide"
)


# ---------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------
ARQUIVO_PADRAO = "Dados atualizados (2).csv"


@st.cache_data
def carregar_dados(arquivo):
    df = pd.read_csv(arquivo)

    # Receita e lucro por unidade/linha
    df["Receita"] = df["preco_venda"] * df["quantidade"]
    df["Lucro_Unitario"] = df["Lucro"] / df["quantidade"]

    # Indicador binário para facilitar os cálculos
    df["is_fancy"] = df["linha"].eq("Fancy")

    return df


def teste_welch_aprox_normal(grupo_a, grupo_b):
    """
    Compara as médias de dois grupos.
    O p-valor usa aproximação normal, suficiente para uma leitura
    estatística no dashboard com as bibliotecas já disponíveis.
    """
    a = np.asarray(grupo_a.dropna(), dtype=float)
    b = np.asarray(grupo_b.dropna(), dtype=float)

    media_a = a.mean()
    media_b = b.mean()

    var_a = a.var(ddof=1)
    var_b = b.var(ddof=1)

    n_a = len(a)
    n_b = len(b)

    erro_padrao = math.sqrt(var_a / n_a + var_b / n_b)
    diferenca = media_a - media_b
    estatistica = diferenca / erro_padrao

    # Aproximação normal bilateral
    p_valor = math.erfc(abs(estatistica) / math.sqrt(2))

    margem = 1.96 * erro_padrao
    ic_inferior = diferenca - margem
    ic_superior = diferenca + margem

    return {
        "media_a": media_a,
        "media_b": media_b,
        "diferenca": diferenca,
        "estatistica": estatistica,
        "p_valor": p_valor,
        "ic_inferior": ic_inferior,
        "ic_superior": ic_superior,
    }


# ---------------------------------------------------------
# CARREGAMENTO
# ---------------------------------------------------------
st.title("✨ Efeito Fancy")
st.markdown(
    "### Fancy Score, evidências matemáticas e recomendação de público-alvo"
)

st.sidebar.header("Filtros")

arquivo_local = Path(ARQUIVO_PADRAO)

if arquivo_local.exists():
    df = carregar_dados(ARQUIVO_PADRAO)
else:
    upload = st.sidebar.file_uploader(
        "Envie o arquivo CSV",
        type=["csv"]
    )

    if upload is None:
        st.info(
            "Coloque o CSV no mesmo repositório do app ou envie o arquivo "
            "pela barra lateral para iniciar a análise."
        )
        st.stop()

    df = carregar_dados(upload)


# ---------------------------------------------------------
# FILTROS
# ---------------------------------------------------------
estados = sorted(df["estado"].dropna().unique())
canais = sorted(df["canal_aquisicao"].dropna().unique())
linhas = sorted(df["linha"].dropna().unique())

filtro_estado = st.sidebar.multiselect(
    "Estado",
    estados,
    default=estados
)

filtro_canal = st.sidebar.multiselect(
    "Canal de aquisição",
    canais,
    default=canais
)

filtro_linha = st.sidebar.multiselect(
    "Linha",
    linhas,
    default=linhas
)

dados = df[
    df["estado"].isin(filtro_estado)
    & df["canal_aquisicao"].isin(filtro_canal)
    & df["linha"].isin(filtro_linha)
].copy()

if dados.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()


# ---------------------------------------------------------
# FANCY SCORE POR CLIENTE
# Regra solicitada pelo professor:
# quantidade de compras Fancy / total de compras * 100
# ---------------------------------------------------------
clientes = (
    dados.groupby("id_cliente")
    .agg(
        total_compras=("id_pedido", "count"),
        compras_fancy=("is_fancy", "sum"),
        receita=("Receita", "sum"),
        lucro=("Lucro", "sum"),
        idade=("idade", "first"),
        renda=("renda_mensal", "first"),
        estado=("estado", "first"),
        canal=("canal_aquisicao", "first"),
    )
    .reset_index()
)

clientes["Fancy Score"] = (
    clientes["compras_fancy"] / clientes["total_compras"] * 100
)

clientes["Faixa Etária"] = pd.cut(
    clientes["idade"],
    bins=[0, 29, 39, 49, 59, 200],
    labels=["18–29", "30–39", "40–49", "50–59", "60+"]
)


# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
score_medio = clientes["Fancy Score"].mean()
percentual_fancy = dados["is_fancy"].mean() * 100
lucro_total = dados["Lucro"].sum()
clientes_analisados = clientes["id_cliente"].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Clientes analisados", f"{clientes_analisados:,}".replace(",", "."))
c2.metric("Fancy Score médio", f"{score_medio:.1f}%")
c3.metric("Compras Fancy", f"{percentual_fancy:.1f}%")
c4.metric("Lucro total", f"R$ {lucro_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


st.divider()


# ---------------------------------------------------------
# 1. FANCY SCORE
# ---------------------------------------------------------
st.header("1. Fancy Score por cliente")

st.markdown(
    """
**Fórmula utilizada:**

**Fancy Score = (compras de itens Fancy ÷ total de compras do cliente) × 100**

Quanto maior o percentual, maior a participação da linha Fancy no comportamento de compra daquele cliente.
"""
)

col1, col2 = st.columns(2)

with col1:
    top_clientes = (
        clientes.sort_values("Fancy Score", ascending=False)
        .head(15)
        .sort_values("Fancy Score")
    )

    fig_top = px.bar(
        top_clientes,
        x="Fancy Score",
        y="id_cliente",
        orientation="h",
        text="Fancy Score",
        title="Top 15 clientes por Fancy Score",
        labels={
            "id_cliente": "Cliente",
            "Fancy Score": "Fancy Score (%)"
        }
    )
    fig_top.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_top.update_xaxes(range=[0, 105])
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    fig_hist = px.histogram(
        clientes,
        x="Fancy Score",
        nbins=20,
        title="Distribuição do Fancy Score",
        labels={"Fancy Score": "Fancy Score (%)", "count": "Clientes"}
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ---------------------------------------------------------
# 2. EFEITO FANCY — EVIDÊNCIA MATEMÁTICA
# ---------------------------------------------------------
st.header("2. O Efeito Fancy existe?")

st.markdown(
    """
Para testar a hipótese, comparamos **preço unitário** e **lucro unitário**
entre produtos Fancy e Padrão.

A lógica é:

> Se a linha Fancy apresentar médias significativamente maiores,
> existe evidência quantitativa de que o posicionamento Fancy está associado
> a maior valor econômico por item.
"""
)

if {"Fancy", "Padrão"}.issubset(set(df["linha"].unique())):

    fancy = dados.loc[dados["linha"] == "Fancy"]
    padrao = dados.loc[dados["linha"] == "Padrão"]

    if len(fancy) > 1 and len(padrao) > 1:

        teste_preco = teste_welch_aprox_normal(
            fancy["preco_venda"],
            padrao["preco_venda"]
        )

        teste_lucro = teste_welch_aprox_normal(
            fancy["Lucro_Unitario"],
            padrao["Lucro_Unitario"]
        )

        # Tabela-resumo
        resumo = pd.DataFrame({
            "Métrica": ["Preço unitário", "Lucro unitário"],
            "Fancy": [
                fancy["preco_venda"].mean(),
                fancy["Lucro_Unitario"].mean()
            ],
            "Padrão": [
                padrao["preco_venda"].mean(),
                padrao["Lucro_Unitario"].mean()
            ]
        })

        resumo["Diferença %"] = (
            (resumo["Fancy"] / resumo["Padrão"]) - 1
        ) * 100

        st.dataframe(
            resumo.style.format({
                "Fancy": "R$ {:.2f}",
                "Padrão": "R$ {:.2f}",
                "Diferença %": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns(2)

        with col1:
            fig_comparacao = go.Figure()

            fig_comparacao.add_trace(
                go.Bar(
                    name="Fancy",
                    x=["Preço unitário", "Lucro unitário"],
                    y=[
                        fancy["preco_venda"].mean(),
                        fancy["Lucro_Unitario"].mean()
                    ]
                )
            )

            fig_comparacao.add_trace(
                go.Bar(
                    name="Padrão",
                    x=["Preço unitário", "Lucro unitário"],
                    y=[
                        padrao["preco_venda"].mean(),
                        padrao["Lucro_Unitario"].mean()
                    ]
                )
            )

            fig_comparacao.update_layout(
                title="Comparação econômica: Fancy x Padrão",
                barmode="group",
                yaxis_title="Valor médio (R$)"
            )

            st.plotly_chart(fig_comparacao, use_container_width=True)

        with col2:
            st.subheader("Teste estatístico")

            st.metric(
                "Diferença no lucro unitário",
                f"R$ {teste_lucro['diferenca']:.2f}"
            )

            st.write(
                f"**IC 95% da diferença:** "
                f"R$ {teste_lucro['ic_inferior']:.2f} a "
                f"R$ {teste_lucro['ic_superior']:.2f}"
            )

            if teste_lucro["p_valor"] < 0.001:
                st.success(
                    "EVIDÊNCIA FORTE DE EFEITO FANCY: "
                    "p < 0,001 e o intervalo de confiança não inclui zero."
                )
            else:
                st.warning(
                    "A diferença observada não atingiu o nível de evidência "
                    "estatística definido para o painel."
                )

            st.caption(
                "O p-valor apresentado utiliza aproximação normal para o teste "
                "de diferença entre médias. A amostra é grande, o que torna "
                "essa aproximação adequada para fins exploratórios do case."
            )

        # Insight automático
        aumento_lucro = (
            fancy["Lucro_Unitario"].mean()
            / padrao["Lucro_Unitario"].mean()
            - 1
        ) * 100

        aumento_preco = (
            fancy["preco_venda"].mean()
            / padrao["preco_venda"].mean()
            - 1
        ) * 100

        st.info(
            f"**Insight:** os itens Fancy apresentam preço unitário médio "
            f"{aumento_preco:.1f}% maior e lucro unitário médio "
            f"{aumento_lucro:.1f}% maior que os itens Padrão."
        )


# ---------------------------------------------------------
# 3. RELAÇÃO ENTRE FANCY SCORE E RESULTADO
# ---------------------------------------------------------
st.header("3. O cliente que compra mais Fancy gera mais valor?")

correlacao_lucro = clientes["Fancy Score"].corr(clientes["lucro"])
correlacao_receita = clientes["Fancy Score"].corr(clientes["receita"])

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Correlação Fancy Score × Lucro",
        f"{correlacao_lucro:.2f}"
    )

with col2:
    st.metric(
        "Correlação Fancy Score × Receita",
        f"{correlacao_receita:.2f}"
    )

scatter = px.scatter(
    clientes,
    x="Fancy Score",
    y="lucro",
    size="total_compras",
    hover_data=["id_cliente", "idade", "canal", "estado"],
    title="Fancy Score x Lucro por cliente",
    labels={
        "Fancy Score": "Fancy Score (%)",
        "lucro": "Lucro do cliente (R$)",
        "total_compras": "Total de compras"
    }
)

st.plotly_chart(scatter, use_container_width=True)


# ---------------------------------------------------------
# 4. PÚBLICO-ALVO
# ---------------------------------------------------------
st.header("4. Qual público o Marketing deve priorizar?")

st.markdown(
    """
A recomendação considera três sinais em conjunto:

1. **Fancy Score alto** → maior afinidade com a linha Fancy;
2. **Lucro médio alto** → maior potencial econômico;
3. **Volume de clientes** → evita recomendar um grupo muito pequeno.
"""
)

# Canal
por_canal = (
    clientes.groupby("canal")
    .agg(
        Clientes=("id_cliente", "count"),
        Fancy_Score=("Fancy Score", "mean"),
        Lucro_Medio=("lucro", "mean")
    )
    .reset_index()
    .sort_values("Fancy_Score", ascending=False)
)

# Faixa etária
por_idade = (
    clientes.groupby("Faixa Etária", observed=True)
    .agg(
        Clientes=("id_cliente", "count"),
        Fancy_Score=("Fancy Score", "mean"),
        Lucro_Medio=("lucro", "mean")
    )
    .reset_index()
    .sort_values("Fancy_Score", ascending=False)
)

col1, col2 = st.columns(2)

with col1:
    fig_canal = px.bar(
        por_canal.sort_values("Fancy_Score"),
        x="Fancy_Score",
        y="canal",
        orientation="h",
        text="Fancy_Score",
        title="Fancy Score médio por canal",
        labels={"Fancy_Score": "Fancy Score médio (%)", "canal": "Canal"}
    )
    fig_canal.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig_canal, use_container_width=True)

with col2:
    fig_idade = px.bar(
        por_idade.sort_values("Fancy_Score"),
        x="Fancy_Score",
        y="Faixa Etária",
        orientation="h",
        text="Fancy_Score",
        title="Fancy Score médio por faixa etária",
        labels={
            "Fancy_Score": "Fancy Score médio (%)",
            "Faixa Etária": "Faixa etária"
        }
    )
    fig_idade.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig_idade, use_container_width=True)


# Cruzamento idade x canal
cruzamento = (
    clientes.groupby(["Faixa Etária", "canal"], observed=True)
    .agg(
        Clientes=("id_cliente", "count"),
        Fancy_Score=("Fancy Score", "mean"),
        Lucro_Medio=("lucro", "mean")
    )
    .reset_index()
)

cruzamento = cruzamento[cruzamento["Clientes"] >= 50].sort_values(
    ["Fancy_Score", "Lucro_Medio"],
    ascending=False
)

st.subheader("Segmentos com maior potencial")

st.dataframe(
    cruzamento.head(10).style.format({
        "Fancy_Score": "{:.1f}%",
        "Lucro_Medio": "R$ {:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

if not cruzamento.empty:
    melhor = cruzamento.iloc[0]

    st.success(
        f"**Recomendação de Marketing:** priorizar o segmento "
        f"**{melhor['Faixa Etária']}** no canal **{melhor['canal']}**, "
        f"que apresenta Fancy Score médio de **{melhor['Fancy_Score']:.1f}%** "
        f"e lucro médio de **R$ {melhor['Lucro_Medio']:.2f} por cliente**."
    )


# ---------------------------------------------------------
# 5. CONCLUSÃO EXECUTIVA
# ---------------------------------------------------------
st.header("5. Data Storytelling — conclusão")

st.markdown(
    f"""
### O que os dados contam?

**1. O Fancy Score mede afinidade.**  
Cada cliente recebe uma pontuação entre 0% e 100%, calculada pela participação
de compras Fancy no total de suas compras. Nesta amostra, o Fancy Score médio
é de **{score_medio:.1f}%**.

**2. O Efeito Fancy aparece no resultado econômico.**  
A comparação entre Fancy e Padrão mostra diferença relevante em preço e lucro
unitário. O teste apresentado no painel permite verificar se essa diferença
é estatisticamente consistente.

**3. Existe relação entre afinidade e valor.**  
O painel mostra a correlação entre Fancy Score, receita e lucro, permitindo
avaliar se clientes mais inclinados ao Fancy também geram maior resultado.

**4. O Marketing deve mirar afinidade + valor.**  
Em vez de impactar toda a base, a estratégia deve priorizar os segmentos com
maior Fancy Score e maior lucro médio, especialmente nos canais digitais que
apresentarem melhor desempenho.

### Decisão sugerida

**Usar o Fancy Score como variável de segmentação para campanhas**, criando
uma estratégia específica para clientes com alta afinidade Fancy e testando
ofertas, comunicação e produtos premium nesses públicos.
"""
)

st.caption(
    "Dashboard desenvolvido em Streamlit + Pandas + Plotly para o estudo de caso."
)
