# Projeto_Case_Efeito_Fancy

GourmetBox DataLab: Análise Estratégica & "Efeito Fancy"Estudo de Caso: Diagnóstico multicanal integrando dados de CRM, ERP e E-commerce para validação estatística da linha Fancy e otimização do ROI de Marketing.

📌 Visão GeralEste projeto unifica as bases operacionais da GourmetBox utilizando Python e Pandas para mapear o comportamento de compra e validar a hipótese do "Efeito Fancy".Por meio de técnicas de Feature Engineering — como o cálculo de Margem Bruta, Ticket Médio e o inédito Fancy Score —, a análise revela como a linha premium impacta a margem da empresa e orienta o direcionamento de mídia paga.🚀 Acesse o Painel InterativoExplore os dados e simule cenários diretamente na nossa aplicação:

👉 Acessar Dashboard no Streamlit Community Cloud
https://projetocaseefeitofancy-jgy8yg8tcl4ptpqhjbkhcf.streamlit.app/


🛠️ Stack TecnológicaCamadaTecnologiaAplicaçãoData EnginePython & PandasUnificação de dados (CRM/ERP/E-commerce), limpeza e Feature EngineeringData VizStreamlit & PlotlyConstrução do dashboard interativo e gráficos dinâmicosVersionamento & CloudGitHub & Streamlit CloudControle de código-fonte e hospedagem contínuaAI Co-pilotGemini & ChatGPTSuporte na arquitetura do dashboard e estruturação do código

📊 Principais Descobertas: O "Efeito Fancy"A integração das bases comprovou quantitativamente a existência do fenômeno a partir de três pilares:Inversão de Consumo por Renda: O Fancy Score é inversamente proporcional à renda. Clientes da faixa de Baixa Renda lideram a penetração da linha premium (37,3%), enquanto o segmento de Alta Renda registra apenas 16,4%.Engajamento Geracional: O público de 18 a 35 anos apresenta um Fancy Score superior a 50%, consolidando-se como o motor de vendas dos produtos de maior margem.Dominância das Redes Visuais: Os canais com maior conversão em itens Fancy são o TikTok (52,3%) e o Instagram (45,2%).

🎯 Direcionamento Estratégico de MarketingCom base nas evidências encontradas, recomendam-se as seguintes ações operacionais:Targeting Prioritário: Concentrar investimentos de mídia no segmento jovem (18 a 35 anos).Distribuição de Verba: Alocar o orçamento de aquisição predominantemente em TikTok Ads e Instagram Ads.Estratégia de Copywriting: Explorar o gatilho de "autocuidado" e "luxo acessível", posicionando os itens Fancy como uma recompensa diária de alto valor percebido.

📁 Estrutura do RepositórioBash

├── data/                  # Datasets brutos e tratados (CSV)
├── notebooks/             # Scripts de tratamento de dados e merge (Google Colab)
├── dashboard_app.py       # Aplicação principal do Streamlit
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação do projeto
