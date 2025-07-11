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
st.set_page_config(page_title="Latin American Intellectuals Network", layout="wide")
st.title("🌎Exploring epistemic influence  through  Wikipedia graph analysis: Gabriela Mistral")

# Load full dataset
@st.cache_data
def load_data():
    return pd.read_csv("latin_american_intellectuals.csv")

df = load_data()

# Sidebar filters
gender_options = ['All'] + sorted(df["Gender"].dropna().unique())
selected_gender = st.sidebar.selectbox("Filter by Gender", gender_options)

# Filter dataframe by gender
if selected_gender != 'All':
    filtered_df = df[df["Gender"] == selected_gender]
else:
    filtered_df = df

# Sidebar selector
selected_person = st.sidebar.selectbox("Choose a person", sorted(filtered_df["Name"].unique()))

wiki = wikipediaapi.Wikipedia(language='en', user_agent='IntellectualsExplorer/1.0')

# Build graph for selected person, connecting only to other known intellectuals
def build_person_graph(person):
    page = wiki.page(person)
    G = nx.DiGraph()
    G.add_node(person)
    incoming = []

    known_people = set(df["Name"])

    if page.exists():
        links = [link for link in page.links.keys() if link in known_people]
        for link in links:
            G.add_edge(person, link)
            sub_page = wiki.page(link)
            if person in sub_page.links:
                G.add_edge(link, person)
                incoming.append(link)
    else:
        st.error(f"Wikipedia page not found for {person}.")
    return G, person, incoming

G, center_node, incoming_links = build_person_graph(selected_person)

# --- 3D Plotly Graph ---
def draw_3d_graph(G, selected_node=None):
    pos = nx.spring_layout(G, dim=3, seed=42)
    xyz = np.array([pos[n] for n in G.nodes()])
    Xn, Yn, Zn = xyz[:, 0], xyz[:, 1], xyz[:, 2]

    Xe, Ye, Ze = [], [], []
    for e in G.edges():
        x0, y0, z0 = pos[e[0]]
        x1, y1, z1 = pos[e[1]]
        Xe += [x0, x1, None]
        Ye += [y0, y1, None]
        Ze += [z0, z1, None]

    edge_trace = go.Scatter3d(x=Xe, y=Ye, z=Ze, mode='lines', line=dict(color='gray', width=2), hoverinfo='none')

    node_color = []
    for node in G.nodes():
        if node == selected_node:
            node_color.append('gold')
        elif G.has_edge(node, selected_node):
            node_color.append('lightcoral')
        elif G.has_edge(selected_node, node):
            node_color.append('lightblue')
        else:
            node_color.append('lightgray')

    node_trace = go.Scatter3d(
        x=Xn, y=Yn, z=Zn,
        mode='markers+text',
        marker=dict(size=8, color=node_color),
        text=list(G.nodes()),
        textposition='top center',
        hoverinfo='text'
    )

    layout = go.Layout(
        title=f"3D Network Centered on {selected_node}",
        showlegend=False,
        margin=dict(l=0, r=0, t=50, b=0),
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    st.plotly_chart(fig, use_container_width=True)

draw_3d_graph(G, center_node)

st.markdown(f"### Wikipedia Page: [🔗 {selected_person}](https://en.wikipedia.org/wiki/{selected_person.replace(' ', '_')})")
st.info(f"📥 Incoming Links: {len(incoming_links)} / Outgoing Links: {len(list(G.edges(center_node)))}")

# --- PyVis Interactive Network ---
st.subheader("🕸️ Interactive Network (PyVis) with Filtering & Physics Controls")

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
        html = open(path, 'r', encoding='latin-1').read()
        components.html(html, height=800, scrolling=True)

visualize_pyvis_network(G)

# --- Adjacency Matrix ---
st.subheader("📀 Adjacency Matrix")
adj_df = pd.DataFrame(nx.to_numpy_array(G, nodelist=G.nodes()), index=G.nodes(), columns=G.nodes())
st.dataframe(adj_df)

# --- Node Properties Table ---
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

# --- 2D Centered Graph ---
st.subheader("🧭 2D Centered View of Network")

def draw_2d_graph(G, selected_node):
    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='gray'),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y, node_color, node_text = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        color = (
            'gold' if node == selected_node else
            'lightcoral' if G.has_edge(node, selected_node) else
            'lightblue' if G.has_edge(selected_node, node) else
            'lightgray'
        )
        node_color.append(color)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(size=10, color=node_color),
        text=node_text,
        textposition='top center',
        hoverinfo='text'
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text='📌 Centered View of Network', font=dict(size=16)),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=50),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)))

    st.plotly_chart(fig, use_container_width=True)

draw_2d_graph(G, center_node)
