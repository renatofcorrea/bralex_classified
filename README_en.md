# 🧠 BrAlex Classified

**BrAlex Classified** is an interactive web application for classifying scientific publications indexed in OpenAlex, using the Brazilian classification systems **CNPq** and **CAPES**.

The tool allows you to:
- Classify works by Broad Area, Area, Subarea, and Subject
- Visualize co-occurrence networks of concepts
- Export results in CSV, GraphML, and GEXF formats
- Explore interactive graphs with zoom, drag, and dynamic physics settings

---

## 🚀 Demo

Access the app here:  
[https://bralexclassified-jzqmv7b8obp7xmbh2br5p9.streamlit.app](https://bralexclassified-jzqmv7b8obp7xmbh2br5p9.streamlit.app)

---

## 📂 Requirements

You can install the dependencies with:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Running Locally

```bash
streamlit run bralex_classified.py
```

---

## 📁 Project Structure

```
📁 bralex_classified/
├── bralex_classified.py
├── compatibility_data_model.json
├── requirements.txt
├── README.md
└── README_en.md
```

---

## ✍️ How to Use

1. Insert the OpenAlex API URL (e.g., filtered by institution)
2. Click on **Start Classification**
3. Preview the table with classified concepts
4. Select the level (Subject, Area, etc.) and click **Create Classification Network**
5. Download the CSV or explore the interactive graph

---

## 🧠 About

This project was created to facilitate the classification and visualization of Brazilian scientific publications using the global OpenAlex database and national classification systems.

Built with ❤ using [Streamlit](https://streamlit.io/).