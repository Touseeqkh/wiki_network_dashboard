import streamlit as st
import pandas as pd
import wikipediaapi
import networkx as nx
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(page_title="Latin American Intellectuals", layout="wide")

st.title("🌎 Latin American Intellectuals: Wikipedia Network Explorer")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_csv("latin_american_intellectuals.csv")

df = load_data()

# Filter by gender
genders = df["Gender"].dropna().unique().tolist()
selected_genders = st.sidebar.multiselect("Select Gender(s)", genders, default=genders)

# Filtered DataFrame
filtered_df = df[df["Gender"].isin(selected_genders)]

# Search individual
names = filtered_df["Name"].dropna().unique().tolist()
selected_name = st.sidebar.selectbox("🔎 Explore Person", ["None"] + sorted(names))

st.markdown("This tool lets you visualize **incoming and outgoing Wikipedia links** and explore gender-based statistics of Latin American intellectuals.")

# --- Visualization Section ---
if selected_name != "None":
    wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='WikipediaNetworkApp/1.0 (touseeqkhanswl@gmail.com)'
    )

    page = wiki.page(selected_name)

    if not page.exists():
        st.error("❌ Wikipedia page not found.")
    else:
        st.subheader(f"🧠 Network for: {selected_name}")

        # Fetch outgoing links
        links = list(page.links.keys())
        G = nx.DiGraph()
        G.add_node(selected_name)

        # Simulate incoming links
        incoming = []
        for link in links[:25]:  # limit for performance
            G.add_edge(selected_name, link)
            sub_page = wiki.page(link)
            if selected_name in sub_page.links:
                G.add_edge(link, selected_name)
                incoming.append(link)

        # PageRank
        pagerank_scores = nx.pagerank(G)
        pos = nx.spring_layout(G, dim=3, seed=42)

        # Nodes and Edges
        xyz = np.array([pos[n] for n in G.nodes()])
        Xn, Yn, Zn = xyz[:, 0], xyz[:, 1], xyz[:, 2]

        Xe, Ye, Ze = [], [], []
        for e in G.edges():
            x0, y0, z0 = pos[e[0]]
            x1, y1, z1 = pos[e[1]]
            Xe += [x0, x1, None]
            Ye += [y0, y1, None]
            Ze += [z0, z1, None]

        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=Xe, y=Ye, z=Ze, mode='lines',
            line=dict(color='gray', width=1),
            hoverinfo='none'))

        fig.add_trace(go.Scatter3d(
            x=Xn, y=Yn, z=Zn,
            mode='markers+text',
            marker=dict(
                size=[pagerank_scores.get(n, 0)*5000 + 4 for n in G.nodes()],
                color=['gold' if n == selected_name else 'seagreen' if n in incoming else 'tomato' for n in G.nodes()],
            ),
            text=list(G.nodes()),
            hoverinfo='text',
            textposition='top center'
        ))

        fig.update_layout(
            title=f"3D Wikipedia Link Network of {selected_name}",
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=False,
            scene=dict(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), zaxis=dict(showgrid=False))
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info(f"📥 Incoming Links Detected: {len(incoming)} / {len(links)} Outgoing")

# --- Statistics Section ---
st.subheader("📊 Gender and Occupation Distribution")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Gender Distribution")
    st.bar_chart(filtered_df["Gender"].value_counts())

with col2:
    st.markdown("### Occupation Distribution")
    st.bar_chart(filtered_df["Occupation"].value_counts())

# --- Connection Listing ---
if selected_name != "None":
    st.subheader(f"🔗 Connections for {selected_name}")
    st.markdown("**Outgoing Links:**")
    st.write(links[:20])
    st.markdown("**Incoming Links (Simulated):**")
    st.write(incoming)
