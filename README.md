# 🧠 BrAlex Classified

**BrAlex Classified** é uma aplicação web interativa para **classificar publicações indexadas no OpenAlex** com base nos sistemas brasileiros de classificação da **CNPq** e do **CAPES**.

A ferramenta permite:
- Classificar artigos por Broad Area, Area, Subarea e Subject
- Visualizar redes de coocorrência de conceitos
- Exportar os resultados em CSV, GraphML e GEXF
- Explorar redes interativas com zoom, arrasto e filtros dinâmicos

---

## 🚀 Demonstração

Acesse aqui (exemplo):
[https://bralex-classified.streamlit.app](https://bralex-classified.streamlit.app)

---

## 📂 Requisitos

Crie um ambiente virtual (opcional) e instale as dependências com:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Executando localmente

```bash
streamlit run bralex_classified.py
```

---

## 📁 Estrutura

```
📁 bralex_classified/
├── bralex_classified.py
├── compatibility_data_model.json
├── requirements.txt
└── README.md
```

---

## ✍️ Exemplo de uso

1. Insira a URL da API do OpenAlex (ex: com filtro por instituição)
2. Clique em **Start Classification**
3. Visualize a tabela de conceitos classificados
4. Selecione um nível (Subject, Area, etc.) e clique em **Create Classification Network**
5. Baixe o CSV ou explore a rede interativa

---

## 🧠 Sobre

Este projeto tem como objetivo facilitar a análise e visualização de trabalhos científicos brasileiros, aproveitando a base global do [OpenAlex](https://openalex.org/) e os sistemas de classificação nacionais.

Desenvolvido com ❤ usando [Streamlit](https://streamlit.io/).