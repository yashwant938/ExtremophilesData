import streamlit as st
import pandas as pd
import re
from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx

# Define the file paths for your data
chemicals_file_path = 'Task3_secondary_metabolites_fungus_Chemicals_pubmed.csv'
genes_file_path = 'Task3_secondary_metabolites_fungus_Genes_pubmed.csv'
interactions_file_path = 'Task11_chemicals_gene.csv'

# Read the chemical, gene, and interactions CSV files into dataframes
chemicals_df = pd.read_csv(chemicals_file_path)
genes_df = pd.read_csv(genes_file_path)
interactions_df = pd.read_csv(interactions_file_path)

def preprocess_sentence(sentence):
    # Remove punctuation and convert to lowercase
    sentence = re.sub(r'[^\w\s]', '', sentence).lower()
    return sentence

# Convert 'Chemicals' column in chemicals_df and 'Genes' column in genes_df to string and preprocess
chemicals_df['Chemicals'] = chemicals_df['Chemicals'].astype(str).apply(preprocess_sentence)
genes_df['Gene'] = genes_df['Gene'].astype(str).apply(preprocess_sentence)

# Preprocess sentences in the interactions dataframe
interactions_df['Sentences'] = interactions_df['Sentences'].astype(str).apply(preprocess_sentence)

# Handle NaN values
chemicals_df.fillna('', inplace=True)
genes_df.fillna('', inplace=True)
interactions_df.fillna('', inplace=True)

# Create dictionaries to store information about chemicals and genes
chemical_info = {name: (chem_id, length, pmid) for chem_id, name, length, pmid in zip(
    chemicals_df['ChemicalsID'], chemicals_df['Chemicals'], chemicals_df['Length'], chemicals_df['PMID']
)}
gene_info = {name: (gene_id, length, pmid) for gene_id, name, length, pmid in zip(
    genes_df['GeneID'], genes_df['Gene'], genes_df['Count'], genes_df['PMID']
)}

# Set the theme to light using Streamlit's config
st.set_page_config(
    page_title="Chemical-Gene Interaction Graph",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "An interactive graph to visualize chemical-gene interactions."
    }
)

# Apply light theme directly in the script
st.markdown(
    """
    <style>
    body {
        background-color: #FFFFFF;
        color: #000000;
    }
    .css-1d391kg, .css-18e3th9 {
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app
st.title("Interactive Graph with Streamlit agraph")

chemicals_list = interactions_df['Chemicals'].unique().tolist()

# Add a search box to select a chemical
selected_chemical = st.selectbox(
    "Select a chemical:",
    options=sorted(chemicals_list),
    format_func=lambda x: x  # Display chemical name as is
)

# Display chemical info in the sidebar
if selected_chemical:
    chem_id, length, pmid = chemical_info[selected_chemical]
    st.sidebar.header("Chemical Information")
    st.sidebar.write(f"**Chemical ID:** {chem_id}")
    st.sidebar.write(f"**Length:** {length}")
    st.sidebar.write(f"**PMID:** {pmid}")

    # Fetch genes interacting with the selected chemical
    filtered_interactions_df = interactions_df[interactions_df['Chemicals'] == selected_chemical]
    interacting_genes = filtered_interactions_df['Gene'].unique()

    # Display gene info in the sidebar
    st.sidebar.header("Interacting Genes Information")
    for gene_name in interacting_genes:
        if gene_name in gene_info:
            gene_id, length, pmid = gene_info[gene_name]
            st.sidebar.write(f"**Gene Name:** {gene_name}")
            st.sidebar.write(f"**Gene ID:** {gene_id}")
            st.sidebar.write(f"**Length:** {length}")
            st.sidebar.write(f"**PMID:** {pmid}")

# Create a directed graph
G = nx.DiGraph()

# Add edges (connections) between chemicals and genes with interaction type as edge attribute
for _, row in filtered_interactions_df.iterrows():
    G.add_edge(row['Chemicals'], row['Gene'], interaction_type=row['interaction_type'])

# Define the nodes and edges for Streamlit agraph
agraph_nodes = [
    Node(id=node, label=node, color='green' if node in chemicals_list else 'blue')
    for node in G.nodes()
]
agraph_edges = [
    Edge(source=edge[0], target=edge[1], label=edge[2]['interaction_type'])
    for edge in G.edges(data=True)
]

# Configure the graph
agraph_config = Config(
    width=1200,
    height=1000,
    directed=True,
    nodeHighlightBehavior=True,
    highlightColor="#F7A7A6",
    collapsible=False,
    node={'labelProperty': 'label'},
    link={'labelProperty': 'label', 'renderLabel': True},
    hierarchical=False,  # Disable hierarchical layout
    animation=True,  # Enable animation
    layout={'improvedLayout': True},  # Use improved layout
    zoom=2.0  # Adjust zoom as needed
)

# Display the graph
agraph(nodes=agraph_nodes, edges=agraph_edges, config=agraph_config)
