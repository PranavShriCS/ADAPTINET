
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from routing.engine import run_adaptinet


st.set_page_config(
    page_title="ADAPTINET",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 ADAPTINET")
st.subheader("ML-Based Congestion Detection and Adaptive Routing")

st.write(
    "Build a network, enter telemetry values, predict congestion, "
    "and compare conventional Dijkstra with ML-assisted routing."
)

FEATURES = [
    ("utilization_percent", "Utilization (%)"),
    ("latency_ms", "Latency (ms)"),
    ("packet_loss_percent", "Packet Loss (%)"),
    ("throughput_mbps", "Throughput (Mbps)"),
    ("queue_occupancy_percent", "Queue Occupancy (%)"),
    ("packet_arrival_rate_pps", "Packet Arrival Rate (pps)")
]


def draw_network(network, predictions, path, title):
    graph = nx.Graph()

    for node, neighbors in network.items():
        graph.add_node(node)

        for neighbor, cost in neighbors.items():
            graph.add_edge(node, neighbor, weight=cost)

    prediction_map = {}

    for item in predictions:
        link = item["link"]

        if isinstance(link, (tuple, list, set, frozenset)):
            prediction_map[frozenset(link)] = item["prediction"]

    positions = nx.spring_layout(graph, seed=42)

    edge_colors = []

    for u, v in graph.edges():
        prediction = prediction_map.get(frozenset((u, v)), 0)
        edge_colors.append(
            "red" if prediction == 1 else "green"
        )

    fig, ax = plt.subplots(figsize=(8, 5))

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_color="#2563eb",
        node_size=1100,
        ax=ax
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        font_color="white",
        font_weight="bold",
        ax=ax
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color=edge_colors,
        width=2.5,
        ax=ax
    )

    edge_labels = nx.get_edge_attributes(graph, "weight")

    nx.draw_networkx_edge_labels(
        graph,
        positions,
        edge_labels=edge_labels,
        ax=ax
    )

    if path and len(path) > 1:
        route_edges = list(zip(path[:-1], path[1:]))

        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=route_edges,
            edge_color="orange",
            width=5,
            ax=ax
        )

    ax.set_title(title)
    ax.axis("off")

    return fig


st.divider()

st.header("1. Network Configuration")

node_input = st.text_input(
    "Enter node names separated by commas",
    placeholder="A, B, C, D, E"
)

nodes = [
    node.strip()
    for node in node_input.split(",")
    if node.strip()
]

if len(nodes) != len(set(nodes)):
    st.error("Node names must be unique.")
    st.stop()

if len(nodes) < 2:
    st.info("Enter at least two nodes to begin.")
    st.stop()

st.success(f"Nodes created: {', '.join(nodes)}")

st.divider()

st.header("2. Link Configuration")

max_links = len(nodes) * (len(nodes) - 1) // 2

link_count = st.number_input(
    "Number of links",
    min_value=1,
    max_value=max_links,
    value=min(len(nodes), max_links),
    step=1
)

network = {node: {} for node in nodes}
links = []
invalid = False

for i in range(int(link_count)):
    st.markdown(f"**Link {i + 1}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        source = st.selectbox(
            "From",
            nodes,
            index=i % len(nodes),
            key=f"from_{i}"
        )

    with col2:
        destination = st.selectbox(
            "To",
            nodes,
            index=(i + 1) % len(nodes),
            key=f"to_{i}"
        )

    with col3:
        cost = st.number_input(
            "Original Cost",
            min_value=0.01,
            value=1.0,
            step=0.5,
            key=f"cost_{i}"
        )

    if source == destination:
        st.error("A node cannot connect to itself.")
        invalid = True
        continue

    if destination in network[source]:
        st.error("Duplicate link detected.")
        invalid = True
        continue

    network[source][destination] = float(cost)
    network[destination][source] = float(cost)

    links.append((source, destination))

if invalid:
    st.warning("Fix invalid links to continue.")
    st.stop()

st.divider()

st.header("3. Telemetry Input")

telemetry = {}

for source, destination in links:
    st.subheader(f"Link {source} — {destination}")

    measurements = {}

    columns = st.columns(3)

    for index, (feature, label) in enumerate(FEATURES):
        maximum = (
            100.0
            if feature in (
                "utilization_percent",
                "packet_loss_percent",
                "queue_occupancy_percent"
            )
            else None
        )

        with columns[index % 3]:
            value = st.number_input(
                label,
                min_value=0.0,
                max_value=maximum,
                value=0.0,
                key=f"{source}_{destination}_{feature}"
            )

            measurements[feature] = float(value)

    telemetry[frozenset((source, destination))] = measurements

st.divider()

st.header("4. Routing Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    start = st.selectbox("Source Node", nodes)

with col2:
    end = st.selectbox(
        "Destination Node",
        nodes,
        index=len(nodes) - 1
    )

with col3:
    alpha = st.number_input(
        "Congestion Penalty (Alpha)",
        min_value=0.0,
        value=6.0,
        step=1.0
    )

st.divider()

if st.button("Run ADAPTINET", type="primary"):

    if start == end:
        st.error("Source and destination must be different.")
        st.stop()

    try:
        result = run_adaptinet(
            network,
            telemetry,
            start,
            end,
            float(alpha)
        )

    except Exception as error:
        st.error(f"Error while running ADAPTINET: {error}")
        st.stop()

    st.header("5. ML Congestion Predictions")

    rows = []

    for item in result["predictions"]:
        link = item["link"]

        if isinstance(link, (tuple, list, set, frozenset)):
            link_name = " - ".join(sorted(map(str, link)))
        else:
            link_name = str(link)

        rows.append({
            "Link": link_name,
            "Congestion": (
                "YES" if item["prediction"] == 1 else "NO"
            ),
            "Original Cost": round(item["original_cost"], 2),
            "Updated Cost": round(item["updated_cost"], 2)
        })

    results_df = pd.DataFrame(rows)

    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True
    )

    congested = sum(
        item["prediction"] == 1
        for item in result["predictions"]
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Links", len(links))
    c2.metric("Congested Links", congested)
    c3.metric("Uncongested Links", len(links) - congested)

    st.divider()

    st.header("6. Routing Comparison")

    conventional = result["conventional_path"]
    adaptive = result["adaptive_path"]

    left, right = st.columns(2)

    with left:
        st.subheader("Conventional Dijkstra")

        st.write(
            " → ".join(conventional)
            if conventional else "No path found"
        )

        st.metric(
            "Original Path Cost",
            f"{result['conventional_cost']:.2f}"
        )

    with right:
        st.subheader("ML-Assisted Routing")

        st.write(
            " → ".join(adaptive)
            if adaptive else "No path found"
        )

        st.metric(
            "Adjusted Path Cost",
            f"{result['adaptive_cost']:.2f}"
        )

    if result["route_changed"]:
        st.success(
            "Adaptive routing selected a different path "
            "based on congestion predictions."
        )
    else:
        st.info("Both routing methods selected the same path.")

    st.caption(
        "Original and adjusted costs use different edge weights. "
        "They do not directly measure real-world latency improvement."
    )

    st.divider()

    st.header("7. Network Visualization")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = draw_network(
            network,
            result["predictions"],
            conventional,
            "Conventional Dijkstra"
        )

        st.pyplot(fig1)
        plt.close(fig1)

    with col2:
        fig2 = draw_network(
            network,
            result["predictions"],
            adaptive,
            "ML-Assisted Adaptive Routing"
        )

        st.pyplot(fig2)
        plt.close(fig2)

    st.divider()

    st.header("8. Link Cost Comparison")

    chart_data = results_df.set_index("Link")[
        ["Original Cost", "Updated Cost"]
    ]

    st.bar_chart(chart_data)

    st.caption(
        "The dashboard generates results dynamically "
        "from the network and telemetry values entered by the user."
    )
