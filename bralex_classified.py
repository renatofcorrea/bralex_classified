import streamlit as st
import pandas as pd
import requests
import json
import networkx as nx
import matplotlib.pyplot as plt
import itertools
from collections import Counter
import re
import community as community_louvain
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import io
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile

import tempfile

def visualizar_grafo_interativo(G):
    if G is None or len(G.nodes) == 0:
        st.warning("The graph is empty or invalid.")
        return

    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)

    net.barnes_hut()  # Layout inicial
    net.toggle_physics(False)  # ❌ Desliga movimento contínuo

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)

        with open(tmp_file.name, 'r', encoding='utf-8') as f:
            html_content = f.read()

        components.html(html_content, height=800, width=1000)



# ----------------------------------
# Funções Auxiliares (do seu código)
# ----------------------------------

def limpar_nome(texto):
    texto_limpo = re.sub(r'[^a-zA-Z0-9_]+', '_', texto)
    texto_limpo = re.sub(r'_+', '_', texto_limpo)
    return texto_limpo.strip('_')

def ajustar_per_page(url_api, per_page=200):
    url_partes = urlparse(url_api)
    query_params = parse_qs(url_partes.query)
    query_params['per_page'] = [str(per_page)]
    nova_query = urlencode(query_params, doseq=True)
    nova_url = urlunparse((
        url_partes.scheme,
        url_partes.netloc,
        url_partes.path,
        url_partes.params,
        nova_query,
        url_partes.fragment
    ))
    return nova_url

def coletar_dados_openalex(url_api):
    dados_artigos = []
    cursor = '*'
    while cursor:
        try:
            response = requests.get(f'{url_api}&cursor={cursor}')
            response.raise_for_status()
        except requests.RequestException as e:
            st.error(f"Error accessing the API: {e}")
            break
        
        resultado = response.json()
        dados_artigos.extend(resultado.get('results', []))
        
        cursor = resultado.get('meta', {}).get('next_cursor', None)
    return dados_artigos

def extrair_niveis(modelo, sistema, mapeamento_conceitos, broad_area="N/A", area="N/A", sub_area="N/A", subject="N/A"):
    if modelo.get('category') == 'broad area':
        broad_area_label = modelo.get(f'{sistema.lower()}_label', 'N/A')
    else:
        broad_area_label = broad_area
    if modelo.get('category') == 'research area':
        area_label = modelo.get(f'{sistema.lower()}_label', 'N/A')
    else:
        area_label = area
    if modelo.get('category') == 'sub area':
        sub_area_label = modelo.get(f'{sistema.lower()}_label', 'N/A')
    else:
        sub_area_label = sub_area
    if modelo.get('category') == 'subject':
        subject_label = modelo.get(f'{sistema.lower()}_label', 'N/A')
    else:
        subject_label = subject

    conceitos = modelo.get('concepts', {})
    for conceito_nome, conceito_info in conceitos.items():
        openalex_list = conceito_info.get('openalex', [])
        for conceito_openalex in openalex_list:
            conceito_id = conceito_openalex.get('id', '').strip().lower()
            if conceito_id:
                mapeamento_conceitos[conceito_id] = {
                    'Broad Area': broad_area_label,
                    'Area': area_label,
                    'Subarea': sub_area_label,
                    'Subject': subject_label
                }

    for sub_modelo in modelo.get('research_areas', []):
        extrair_niveis(sub_modelo, sistema, mapeamento_conceitos, broad_area=broad_area_label)
    for sub_modelo in modelo.get('sub_areas', []):
        extrair_niveis(sub_modelo, sistema, mapeamento_conceitos, broad_area=broad_area_label, area=area_label)
    for sub_modelo in modelo.get('subjects', []):
        extrair_niveis(sub_modelo, sistema, mapeamento_conceitos, broad_area=broad_area_label, area=area_label, sub_area=sub_area_label)

def extrair_valores_unicos(valores_str):
    if valores_str == 'N/A' or pd.isna(valores_str):
        return []
    valores = [parte.strip() for parte in valores_str.split(';')]
    valores_limpos = []
    for valor in valores:
        match = re.match(r'^(.*?)\s*\(', valor)
        if match:
            valores_limpos.append(match.group(1).strip())
        else:
            valores_limpos.append(valor.strip())
    return list(set(valores_limpos))

def gerar_grafo_coocorrencia(df_csv_final, sistema, nivel='Subject'):
    df_filtrado = df_csv_final.copy()
    coluna_nivel = f'{nivel} ({sistema})'

    if coluna_nivel not in df_filtrado.columns:
        st.error(f"Level {nivel} not found in the dataframe!")
        return None

    pares = []
    for valores_str in df_filtrado[coluna_nivel]:
        valores = extrair_valores_unicos(valores_str)
        if len(valores) > 1:
            combinacoes = list(itertools.combinations(valores, 2))
            pares.extend(combinacoes)

    cooccurrence_counter = Counter(pares)
    filtered_edges = {pair: weight for pair, weight in cooccurrence_counter.items()}

    if not filtered_edges:
        st.warning(f"No co-occurrence found for level {nivel}.")
        return None

    G = nx.Graph()
    all_nodes = set(itertools.chain.from_iterable(filtered_edges.keys()))
    G.add_nodes_from(all_nodes)

    for (node1, node2), weight in filtered_edges.items():
        G.add_edge(node1, node2, weight=weight)

    partition = community_louvain.best_partition(G)
    comunidades = set(partition.values())

    color_map = {}
    palette = plt.get_cmap('tab20')
    for idx, comunidade in enumerate(comunidades):
        color_map[comunidade] = palette(idx % 20)

    node_colors = [color_map[partition[node]] for node in G.nodes()]
    degrees = dict(G.degree())
    node_sizes = [degrees[node] * 250 for node in G.nodes()]

    num_nodes = len(G.nodes())

    if num_nodes < 100:
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, k=2.0, iterations=500)

    plt.figure(figsize=(30, 24))
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.85)
    edges = G.edges(data=True)
    edge_weights = [d['weight'] * 0.5 for (_, _, d) in edges]
    nx.draw_networkx_edges(G, pos, edgelist=edges, width=edge_weights, alpha=0.3)

    labels_importantes = {node: node for node, degree in degrees.items() if degree > 3}
    nx.draw_networkx_labels(G, pos, labels=labels_importantes, font_size=14)

    plt.title(f"Co-occurrence Graph ({nivel}) - System {sistema}", fontsize=20)
    plt.axis('off')
    st.pyplot(plt)

    return G

def salvar_grafo(G):
    graphml_file = io.BytesIO()
    gexf_file = io.BytesIO()

    nx.write_graphml(G, graphml_file)
    nx.write_gexf(G, gexf_file)

    graphml_file.seek(0)
    gexf_file.seek(0)

    return graphml_file, gexf_file

# ----------------------------------
# Streamlit App Interface
# ----------------------------------

st.title("CNPq/CAPES Classification System of OpenAlex Works")

st.markdown("### Search the OpenAlex works to be classified")
st.markdown("Use the web search interface: [https://openalex.org/](https://openalex.org/)")
st.markdown("Or create an API request: [https://docs.openalex.org/how-to-use-the-api/api-overview](https://docs.openalex.org/how-to-use-the-api/api-overview)")

url_api_input = st.text_input("Insert the OpenAlex API URL:")

sistema = st.radio("Select the Brazilian classification system:", ["CNPq", "CAPES"])

try:
    with open("compatibility_data_model.json", "r", encoding="utf-8") as f:
        modelo_classificacao = json.load(f)
    st.success("Compatibility data model loaded automatically.")
except FileNotFoundError:
    modelo_classificacao = None
    st.error("Model file not found. Please make sure 'compatibility_data_model.json' is in the same folder as the app.")

if st.button("Start Classification"):
    if not url_api_input or not modelo_classificacao:
        st.error("Enter the OpenAlex API URL and load the classification model!")
    else:
        with st.spinner("Classifying..."):
            url_api = ajustar_per_page(url_api_input, per_page=200)
            dados_artigos = coletar_dados_openalex(url_api)

            mapeamento_conceitos = {}
            for area in modelo_classificacao:
                extrair_niveis(area, sistema, mapeamento_conceitos)

            linhas_csv = []
            for artigo in dados_artigos:
                artigo_id = artigo.get('id', 'N/A')
                conceitos = [concept.get('display_name') for concept in artigo.get('concepts', [])]
                conceitos_ids = [concept.get('id', '').strip().lower() for concept in artigo.get('concepts', [])]

                for conceito, conceito_id in zip(conceitos, conceitos_ids):
                    classificacao = mapeamento_conceitos.get(conceito_id, {})
                    linhas_csv.append({
                        'ID do Artigo': artigo_id,
                        'Conceitos': conceito,
                        f'Broad Area ({sistema})': classificacao.get('Broad Area', 'N/A'),
                        f'Area ({sistema})': classificacao.get('Area', 'N/A'),
                        f'Subarea ({sistema})': classificacao.get('Subarea', 'N/A'),
                        f'Subject ({sistema})': classificacao.get('Subject', 'N/A')
                    })

            df_csv = pd.DataFrame(linhas_csv)
            df = df_csv[df_csv[f'Broad Area ({sistema})'] != 'N/A']
            artigos_agrupados = df.groupby('ID do Artigo')

            def formatar_com_score(frequencias, total):
                frequencias = {k: v for k, v in frequencias.items() if k != 'N/A'}
                if total == 0 or not frequencias:
                    return 'N/A'
                return '; '.join([f'{chave} ({valor/total:.2f})' for chave, valor in frequencias.items()])

            linhas_csv_final = []
            for artigo_id, grupo in artigos_agrupados:
                conceitos = '; '.join(grupo['Conceitos'].unique())
                total_conceitos = grupo.shape[0]

                linhas_csv_final.append({
                    'work_id': artigo_id,
                    'concepts': conceitos,
                    f'Broad Area ({sistema})': formatar_com_score(grupo[f'Broad Area ({sistema})'].value_counts().to_dict(), total_conceitos),
                    f'Area ({sistema})': formatar_com_score(grupo[f'Area ({sistema})'].value_counts().to_dict(), total_conceitos),
                    f'Subarea ({sistema})': formatar_com_score(grupo[f'Subarea ({sistema})'].value_counts().to_dict(), total_conceitos),
                    f'Subject ({sistema})': formatar_com_score(grupo[f'Subject ({sistema})'].value_counts().to_dict(), total_conceitos)
                })

            df_csv_final = pd.DataFrame(linhas_csv_final).fillna('N/A')
            colunas_classificacao = [f'Broad Area ({sistema})', f'Area ({sistema})', f'Subarea ({sistema})', f'Subject ({sistema})']
            df_csv_final = df_csv_final[
                ~df_csv_final[colunas_classificacao].apply(lambda x: x.str.contains('N/A')).any(axis=1)
            ]

            st.success("Classification completed!")
            
            # Store dataframe in session state
            st.session_state['df_csv_final'] = df_csv_final

# Garantir inicialização no topo do código
if 'df_csv_final' not in st.session_state:
    st.session_state['df_csv_final'] = None

if 'grafo_gerado' not in st.session_state:
    st.session_state['grafo_gerado'] = None

# Exibir resultados apenas quando existir df
if st.session_state['df_csv_final'] is not None:
    st.dataframe(st.session_state['df_csv_final'])

    nivel = st.selectbox("Select the level for the network:", ["Broad Area", "Area", "Subarea", "Subject"])

    if st.button("Create Classification Network"):
        G = gerar_grafo_coocorrencia(st.session_state['df_csv_final'], sistema, nivel=nivel)
        if G:
            st.session_state['grafo_gerado'] = G

    if st.session_state['grafo_gerado'] is not None:
        graphml_file, gexf_file = salvar_grafo(st.session_state['grafo_gerado'])

        st.download_button("Download GraphML", graphml_file, file_name="graph.graphml")
        st.download_button("Download GEXF", gexf_file, file_name="graph.gexf")

    # Botão para abrir o grafo interativo
        if st.button("Visualize Interactive Network (Zoom/Pan Enabled)"):
            visualizar_grafo_interativo(st.session_state['grafo_gerado'])


    # Só exibe se houver DataFrame válido!
    st.download_button(
        "Export results (CSV)",
        st.session_state['df_csv_final'].to_csv(index=False, sep=';', encoding='utf-8-sig'),
        file_name="classified_results.csv"
    )
else:
    st.warning("Please run the classification first to generate results!")
