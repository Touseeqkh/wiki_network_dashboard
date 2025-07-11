import streamlit as st
import pandas as pd
import wikipediaapi
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

# --- Page Config ---
st.set_page_config(page_title="Gabriela Mistral Network 3D + PyVis", layout="wide")

st.title("🌎 Gabriela Mistral: Wikipedia Network Explorer with 3D & PyVis")

# Load dataset filtered for Gabriela Mistral
@st.cache_data
def load_data():
    df = pd.read_csv("latin_american_intellectuals.csv")
    return df[df["Name"] == "Gabriela Mistral"]

df = load_data()

wiki = wikipediaapi.Wikipedia(language='en', user_agent='GabrielaMistralExplorer/1.0')

# Build graph function for Gabriela Mistral
def build_gabriela_graph():
    person = "Gabriela Mistral"
    page = wiki.page(person)
    G = nx.DiGraph()
    G.add_node(person)
    incoming = []

    if page.exists():
        links = list(page.links.keys())[:25]
        for link in links:
            G.add_edge(person, link)
            sub_page = wiki.page(link)
            if person in sub_page.links:
                G.add_edge(link, person)
                incoming.append(link)
    else:
        st.error("Wikipedia page not found for Gabriela Mistral.")
    return G, person, incoming

G, center_node, incoming_links = build_gabriela_graph()

# 3D Plotly Graph with Gabriela Mistral centered
def draw_3d_graph(G, selected_node=None):
    pos = nx.spring_layout(G, dim=3, seed=42)
    
    xyz = np.array([pos[n] for n in G.nodes()])
    Xn, Yn, Zn = xyz[:,0], xyz[:,1], xyz[:,2]
    
    Xe, Ye, Ze = [], [], []
    for e in G.edges():
        x0, y0, z0 = pos[e[0]]
        x1, y1, z1 = pos[e[1]]
        Xe += [x0, x1, None]
        Ye += [y0, y1, None]
        Ze += [z0, z1, None]
        
    edge_trace = go.Scatter3d(x=Xe, y=Ye, z=Ze,
                              mode='lines',
                              line=dict(color='gray', width=2),
                              hoverinfo='none')
    
    node_color = []
    for node in G.nodes():
        if node == selected_node:
            node_color.append('gold')
        elif G.has_edge(node, selected_node):
            node_color.append('lightcoral')  # incoming
        elif G.has_edge(selected_node, node):
            node_color.append('lightblue')  # outgoing
        else:
            node_color.append('lightgray')
            
    node_trace = go.Scatter3d(x=Xn, y=Yn, z=Zn,
                              mode='markers+text',
                              marker=dict(size=8, color=node_color),
                              text=list(G.nodes()),
                              textposition='top center',
                              hoverinfo='text')
    
    layout = go.Layout(title=f"3D Network Centered on {selected_node}",
                       showlegend=False,
                       margin=dict(l=0, r=0, t=50, b=0),
                       scene=dict(xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                  yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                  zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    
    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    st.plotly_chart(fig, use_container_width=True)

draw_3d_graph(G, center_node)

st.markdown(f"### Wikipedia Page: [🔗 Gabriela Mistral](https://en.wikipedia.org/wiki/Gabriela_Mistral)")

st.info(f"📥 Incoming Links: {len(incoming_links)} / Outgoing Links: {len(list(G.edges(center_node)))}")

# --- PyVis Interactive Network ---

def visualize_pyvis_network(G):
    net = Network(notebook=True,
                  cdn_resources="remote",
                  bgcolor="#222222",
                  font_color="white",
                  height="750px",
                  width="100%",
                  select_menu=True,
                  filter_menu=True)
    
    for node in G.nodes():
        title = f"<b>{node}</b>"
        net.add_node(node, label=node, title=title)
    for source, target in G.edges():
        net.add_edge(source, target)
    
    net.show_buttons(filter_=['physics'])
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "pyvis_graph.html")
        net.save_graph(path)
        html = open(path, 'r', encoding='utf-8').read()
        components.html(html, height=800, scrolling=True)

st.subheader("🕸️ Interactive Network (PyVis) with Filtering & Physics Controls")
visualize_pyvis_network(G)

# --- Adjacency Matrix ---
st.subheader("📀 Adjacency Matrix")
adj_df = pd.DataFrame(nx.to_numpy_array(G, nodelist=G.nodes()), index=G.nodes(), columns=G.nodes())
st.dataframe(adj_df)

# --- Node Properties ---
st.subheader("📋 Node Properties")
summary = []
for node in G.nodes():
    record = df[df["Name"] == node].to_dict(orient='records')
    summary.append({
        "Name": node,
        "Gender": record[0]["Gender"] if record else "Unknown",
        "Nationality": record[0]["Nationality"] if record else "Unknown",
        "Birthdate": record[0]["Birthdate"] if record else "Unknown",
        "Occupation": record[0]["Occupation"] if record else "Unknown",
        "Prize": record[0]["Prize"] if record and "Prize" in record[0] else "None"
    })
st.dataframe(pd.DataFrame(summary))
