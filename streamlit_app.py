import streamlit as st
import networkx as nx
import pandas as pd
import plotly.graph_objs as go
import wikipediaapi
import numpy as np

# --- Load CSV for gender filtering ---
df = pd.read_csv("latin_american_intellectuals.csv")
people_set = set(df["Name"].dropna().unique())

# --- Sidebar: Select Person ---
st.sidebar.title("Wikipedia Person Network")
selected_person = st.sidebar.selectbox("Select a Person", sorted(people_set))
selected_genders = st.sidebar.multiselect("Filter by Gender", df["Gender"].dropna().unique())
max_links = st.sidebar.slider("Max Links to Explore", min_value=10, max_value=2000, value=1000, step=10)

# --- Fetch Wikipedia Network ---
st.title(f"🧠 Network for: {selected_person}")
st.write("Fetching incoming and outgoing links from Wikipedia...")

wiki = wikipediaapi.Wikipedia(language="en", user_agent="WikiNetworkExplorer/1.0 (touseeqkhanswl@example.com)")
page = wiki.page(selected_person)

G = nx.DiGraph()
G.add_node(selected_person)

outgoing_links = list(page.links.keys())[:max_links]

incoming_links = []
for link in outgoing_links:
    try:
        linked_page = wiki.page(link)
        if selected_person in linked_page.links:
            G.add_edge(link, selected_person)
            incoming_links.append(link)
    except:
        continue

for link in outgoing_links:
    G.add_edge(selected_person, link)

# --- Filter only nodes present in CSV people list ---
filtered_nodes = set(G.nodes()).intersection(people_set)
G = G.subgraph(filtered_nodes).copy()

# --- Filter by Gender ---
if selected_genders:
    gender_filtered_names = df[df["Gender"].isin(selected_genders)]["Name"].values
    G = G.subgraph(set(G.nodes()).intersection(gender_filtered_names)).copy()

# --- Compute PageRank ---
pagerank_scores = nx.pagerank(G) if len(G) > 0 else {}

# --- Draw with Plotly 3D ---
if len(G.nodes) > 0:
    st.success(f"Graph has {len(G.nodes)} nodes and {len(G.edges)} edges.")
    pos = nx.spring_layout(G, dim=3, seed=42)
    xyz = np.array([pos[v] for v in G.nodes()])
    Xn, Yn, Zn = xyz[:, 0], xyz[:, 1], xyz[:, 2]

    Xe, Ye, Ze = [], [], []
    for e in G.edges():
        x0, y0, z0 = pos[e[0]]
        x1, y1, z1 = pos[e[1]]
        Xe += [x0, x1, None]
        Ye += [y0, y1, None]
        Ze += [z0, z1, None]

    edge_trace = go.Scatter3d(x=Xe, y=Ye, z=Ze,
        mode='lines', line=dict(color='gray', width=1), hoverinfo='none')

    node_trace = go.Scatter3d(x=Xn, y=Yn, z=Zn,
        mode='markers+text',
        text=[f"{node}<br>PageRank: {pagerank_scores.get(node,0):.4f}" for node in G.nodes()],
        textposition='top center',
        marker=dict(size=[pagerank_scores.get(n, 0) * 50 + 5 for n in G.nodes()], color='skyblue'),
        hoverinfo='text')

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        title=f"3D Wikipedia Network: {selected_person}",
        margin=dict(l=0, r=0, b=0, t=50),
        scene=dict(xaxis=dict(showgrid=False),
                   yaxis=dict(showgrid=False),
                   zaxis=dict(showgrid=False))
    ))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No nodes available after filtering. Try changing filters or person.")

# --- Optional: Show metrics table ---
if len(G) > 0:
    degrees = dict(G.degree())
    data = []
    for node in G.nodes():
        gender = df[df["Name"] == node]["Gender"].values[0] if node in df["Name"].values else "Unknown"
        occ = df[df["Name"] == node]["Occupation"].values[0] if node in df["Name"].values else "Unknown"
        data.append({
            "Name": node,
            "Gender": gender,
            "Occupation": occ,
            "In-Degree": G.in_degree(node),
            "Out-Degree": G.out_degree(node),
            "PageRank": round(pagerank_scores.get(node, 0), 5)
        })

    st.subheader("📊 Node Metrics")
    st.dataframe(pd.DataFrame(data).sort_values("PageRank", ascending=False))
