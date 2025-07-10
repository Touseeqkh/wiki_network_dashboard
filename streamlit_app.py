import streamlit as st
import pandas as pd
import wikipediaapi
import networkx as nx
import plotly.graph_objects as go
import numpy as np

# --- Page setup ---
st.set_page_config(page_title="Latin American Intellectuals Network", layout="wide")
st.title("🌎 Latin American Intellectuals: Wikipedia Network Explorer")

# --- Load CSV dataset ---
@st.cache_data
def load_data():
    return pd.read_csv("latin_american_intellectuals.csv")

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("🔍 Filters")

# Multi-select filters for Gender, Occupation, Nationality
genders = df["Gender"].dropna().unique().tolist()
occupations = df["Occupation"].dropna().unique().tolist()
nationalities = df["Nationality"].dropna().unique().tolist()

selected_genders = st.sidebar.multiselect("Select Gender(s)", genders, default=genders)
selected_occupations = st.sidebar.multiselect("Select Occupation(s)", occupations, default=occupations)
selected_nationalities = st.sidebar.multiselect("Select Nationality(s)", nationalities, default=nationalities)

# Slider for max links to explore (performance tuning)
max_links = st.sidebar.slider("Max Wikipedia links to explore", min_value=10, max_value=1000, value=100, step=10)

# Filter dataset to include only those matching ANY of the selected filters
filtered_df = df[
    (df["Gender"].isin(selected_genders)) |
    (df["Occupation"].isin(selected_occupations)) |
    (df["Nationality"].isin(selected_nationalities))
]

# Names available after filtering
available_names = filtered_df["Name"].dropna().unique().tolist()

selected_name = st.sidebar.selectbox("🔎 Select a Person to explore", ["None"] + sorted(available_names))

# --- Description ---
st.markdown("""
This tool visualizes **incoming and outgoing Wikipedia links** for Latin American intellectuals.
Use the filters to narrow down by Gender, Occupation, and Nationality.
The network graph shows relationships where nodes are people and edges are Wikipedia links.
""")

# --- Main visualization ---
if selected_name != "None":
    wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='WikipediaNetworkApp/1.0 (touseeqkhanswl@gmail.com)'
    )

    page = wiki.page(selected_name)
    if not page.exists():
        st.error(f"❌ Wikipedia page for '{selected_name}' not found.")
    else:
        st.subheader(f"🧠 Network for: {selected_name}")

        # Get outgoing links from the selected page (limited for performance)
        outgoing_links = list(page.links.keys())[:max_links]

        # Build directed graph
        G = nx.DiGraph()
        G.add_node(selected_name)

        incoming_links = []

        # Add outgoing edges and identify incoming links
        for link in outgoing_links:
            G.add_edge(selected_name, link)  # selected -> linked (outgoing)

            sub_page = wiki.page(link)
            # Check if this link references back to selected person (incoming)
            if selected_name in sub_page.links:
                G.add_edge(link, selected_name)  # linked -> selected (incoming)
                incoming_links.append(link)

        # --- Filter graph nodes: keep only those in CSV with ANY of the selected attributes ---
        # Explanation: We want only nodes for which at least one attribute is present
        valid_names = df[
            df["Name"].notna() & (
                df["Gender"].notna() |
                df["Occupation"].notna() |
                df["Nationality"].notna()
            )
        ]["Name"].unique()

        # Keep only graph nodes that are in valid_names (intersection)
        G = G.subgraph(set(G.nodes()).intersection(valid_names)).copy()

        # Further filter graph nodes by selected filters (Gender, Occupation, Nationality)
        filtered_names = filtered_df["Name"].unique()
        G = G.subgraph(set(G.nodes()).intersection(filtered_names)).copy()

        # Compute PageRank for node importance
        if len(G) > 0:
            pagerank_scores = nx.pagerank(G)
        else:
            pagerank_scores = {}

        # Layout for 3D graph
        if len(G) > 0:
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

            # Edges trace
            edge_trace = go.Scatter3d(
                x=Xe, y=Ye, z=Ze,
                mode='lines',
                line=dict(color='gray', width=1),
                hoverinfo='none'
            )

            # Nodes trace with color and size by PageRank
            node_colors = []
            for n in G.nodes():
                if n == selected_name:
                    node_colors.append('gold')
                elif n in incoming_links:
                    node_colors.append('seagreen')
                else:
                    node_colors.append('tomato')

            node_sizes = [pagerank_scores.get(n, 0)*500 + 5 for n in G.nodes()]

            node_trace = go.Scatter3d(
                x=Xn, y=Yn, z=Zn,
                mode='markers+text',
                marker=dict(size=node_sizes, color=node_colors),
                text=[f"{n}<br>PageRank: {pagerank_scores.get(n, 0):.4f}" for n in G.nodes()],
                hoverinfo='text',
                textposition='top center'
            )

            # Figure setup
            fig = go.Figure(data=[edge_trace, node_trace])
            fig.update_layout(
                title=f"3D Wikipedia Link Network: {selected_name}",
                margin=dict(l=0, r=0, t=50, b=0),
                showlegend=False,
                scene=dict(
                    xaxis=dict(showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(showgrid=False, zeroline=False, visible=False),
                    zaxis=dict(showgrid=False, zeroline=False, visible=False)
                )
            )
            st.plotly_chart(fig, use_container_width=True)

            # Info on graph size
            st.info(f"Graph has {len(G.nodes)} nodes and {len(G.edges)} edges.")
            st.info(f"Incoming links (edges into {selected_name}): {len(incoming_links)}")
            st.info(f"Outgoing links (edges from {selected_name}): {len(outgoing_links)}")

            # --- Node metrics table ---
            data = []
            for node in G.nodes():
                gender = df[df["Name"] == node]["Gender"].values[0] if node in df["Name"].values else "Unknown"
                occ = df[df["Name"] == node]["Occupation"].values[0] if node in df["Name"].values else "Unknown"
                nat = df[df["Name"] == node]["Nationality"].values[0] if node in df["Name"].values else "Unknown"
                data.append({
                    "Name": node,
                    "Gender": gender,
                    "Occupation": occ,
                    "Nationality": nat,
                    "In-Degree": G.in_degree(node),
                    "Out-Degree": G.out_degree(node),
                    "PageRank": round(pagerank_scores.get(node, 0), 5)
                })

            st.subheader("📊 Node Metrics")
            st.dataframe(pd.DataFrame(data).sort_values("PageRank", ascending=False))

            # Show connections lists
            st.subheader(f"🔗 Connections for {selected_name}")
            st.markdown("**Outgoing Links (limited):**")
            st.write(outgoing_links[:20])
            st.markdown("**Incoming Links (limited):**")
            st.write(incoming_links[:20])

        else:
            st.warning("No nodes available after filtering. Try changing filters or the selected person.")

# --- Statistics Section for the filtered dataset ---
st.subheader("📊 Gender, Occupation, and Nationality Distribution (Filtered)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Gender Distribution")
    st.bar_chart(filtered_df["Gender"].value_counts())

with col2:
    st.markdown("### Occupation Distribution")
    st.bar_chart(filtered_df["Occupation"].value_counts())

with col3:
    st.markdown("### Nationality Distribution")
    st.bar_chart(filtered_df["Nationality"].value_counts())
