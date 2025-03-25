# 🧠 BrAlex Classified

**BrAlex Classified** é uma aplicação web interativa para **classificar publicações indexadas no OpenAlex** com base nos sistemas brasileiros de classificação de áreas do conhecimento do **CNPq** e da **CAPES**.

A ferramenta permite:
- Classificar artigos por grande área, área, subárea e especialidade
- Visualizar redes de coocorrência de áreas nos quatro níveis
- Exportar os resultados em CSV, GraphML e GEXF
- Explorar redes interativas 

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

1. Insira a URL da API do OpenAlex (ex: com filtro por autor, instituição, ano ou busca por palavras-chave)
2. Clique em **Start Classification**
3. Visualize a tabela de conceitos classificados
4. Selecione um nível (Subject, Area, etc.) e clique em **Create Classification Network**
5. Baixe o CSV ou explore a rede interativa

---

## 🧠 Sobre

Este projeto tem como objetivo facilitar a avaliação de publicações científicos indexadas no [OpenAlex](https://openalex.org/) a partir de dois sistemas brasileiros de classificação de áreas do conhecimento. 

Desenvolvido por meio do [Streamlit](https://streamlit.io/).
