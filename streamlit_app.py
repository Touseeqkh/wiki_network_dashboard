import streamlit as st
import wikipediaapi
import networkx as nx
import plotly.graph_objs as go
import numpy as np

# --------------- Helper: Detect if a page is likely a person ---------------
def is_probably_person(title):
    return (
        isinstance(title, str)
        and " " in title
        and title.istitle()
        and "(" not in title
        and "," not in title
    )

# --------------- Fetch links: outgoing and simulated incoming ---------------
def fetch_links(person):
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="WikipediaNetworkApp/1.0 (touseeqkhanswl@gmail.com)"
    )
    page = wiki.page(person)
    if not page.exists():
        return [], []

    outgoing_links = list(page.links.keys())
    incoming_links = []

    for link in outgoing_links[:30]:  # Limit to 30 for performance
        try:
            linked_page = wiki.page(link)
            if person in linked_page.links:
                incoming_links.append(link)
        except Exception:
            continue

    return outgoing_links, incoming_links

# --------------- Build filtered network graph ---------------
def build_graph(person, outgoing, incoming, show_out=True, show_in=True):
    G = nx.DiGraph()
    G.add_node(person)

    if show_out:
        for link in outgoing:
            if is_probably_person(link):
                G.add_node(link)
                G.add_edge(person, link)

    if show_in:
        for link in incoming:
            if is_probably_person(link):
                G.add_node(link)
                G.add_edge(link, person)

    return G

# --------------- Draw 3D network using Plotly ---------------
def draw_3d_graph(G):
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

    edge_trace = go.Scatter3d(
        x=Xe, y=Ye, z=Ze,
        mode='lines',
        line=dict(color='gray', width=1),
        hoverinfo='none'
    )

    node_trace = go.Scatter3d(
        x=Xn, y=Yn, z=Zn,
        mode='markers+text',
        text=[node for node in G.nodes()],
        textposition='top center',
        marker=dict(size=6, color='skyblue'),
        hoverinfo='text'
    )

    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
            title="🧠 Wikipedia Person Network",
            titlefont_size=20,
            margin=dict(l=0, r=0, b=0, t=40),
            showlegend=False,
            scene=dict(
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                zaxis=dict(showgrid=False)
            )
        )
    )
    return fig

# --------------- Streamlit App Interface ---------------
st.set_page_config(page_title="Wikipedia Person Network", layout="wide")
st.title("🔗 Wikipedia Person Network Dashboard")

person = st.text_input("Enter a Wikipedia person name:", "Gabriela Mistral")

col1, col2 = st.columns(2)
with col1:
    show_outgoing = st.checkbox("Show Outgoing People", value=True)
with col2:
    show_incoming = st.checkbox("Show Incoming People", value=True)

if person:
    with st.spinner(f"Fetching Wikipedia data for '{person}'..."):
        out_links, in_links = fetch_links(person)
        G = build_graph(person, out_links, in_links, show_outgoing, show_incoming)

        if G.number_of_nodes() > 1:
            try:
                pagerank_scores = nx.pagerank(G)
            except Exception:
                pagerank_scores = {node: 1 / G.number_of_nodes() for node in G.nodes()}

            # Display Top 10 PageRank scores
            st.subheader("📊 Top PageRank Nodes")
            top_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            st.table({
                "Node": [n for n, _ in top_nodes],
                "PageRank": [round(s, 4) for _, s in top_nodes]
            })

            # Draw Graph
            st.subheader("🌐 Interactive 3D Graph")
            st.plotly_chart(draw_3d_graph(G), use_container_width=True)
        else:
            st.warning("Not enough linked people to visualize the network.")
else:
    st.info("Enter a valid person’s name from Wikipedia to begin.")
