
from routing.engine import run_adaptinet

FEATURES = [
    ("utilization_percent", "Utilization (%)"),
    ("latency_ms", "Latency (ms)"),
    ("packet_loss_percent", "Packet loss (%)"),
    ("throughput_mbps", "Throughput (Mbps)"),
    ("queue_occupancy_percent", "Queue occupancy (%)"),
    ("packet_arrival_rate_pps", "Packet arrival rate (pps)")
]


def read_int(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = int(input(prompt))

            if minimum is not None and value < minimum:
                print(f"Enter a value >= {minimum}.")
                continue

            if maximum is not None and value > maximum:
                print(f"Enter a value <= {maximum}.")
                continue

            return value

        except ValueError:
            print("Please enter a valid integer.")


def read_float(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = float(input(prompt))

            if value != value or value in (float("inf"), float("-inf")):
                print("Enter a finite number.")
                continue

            if minimum is not None and value < minimum:
                print(f"Enter a value >= {minimum}.")
                continue

            if maximum is not None and value > maximum:
                print(f"Enter a value <= {maximum}.")
                continue

            return value

        except ValueError:
            print("Please enter a valid number.")


def collect_nodes():
    count = read_int("\nNumber of nodes: ", minimum=2)
    nodes = []

    for i in range(count):
        while True:
            node = input(f"Name of node {i + 1}: ").strip()

            if not node:
                print("Node name cannot be empty.")
            elif node in nodes:
                print("Node already exists.")
            else:
                nodes.append(node)
                break

    return nodes


def collect_links(nodes):
    maximum_links = len(nodes) * (len(nodes) - 1) // 2

    count = read_int(
        "\nNumber of links: ",
        minimum=1,
        maximum=maximum_links
    )

    network = {node: {} for node in nodes}
    links = []

    for i in range(count):
        print(f"\n--- Link {i + 1} ---")

        while True:
            source = input("First node: ").strip()
            destination = input("Second node: ").strip()

            if source not in network or destination not in network:
                print("Both nodes must exist.")
            elif source == destination:
                print("A link must connect different nodes.")
            elif destination in network[source]:
                print("This link already exists.")
            else:
                break

        cost = read_float(
            "Original link cost: ",
            minimum=0.000001
        )

        network[source][destination] = cost
        network[destination][source] = cost

        links.append((source, destination))

    return network, links


def collect_telemetry(links):
    telemetry = {}

    print("\n========== NETWORK TELEMETRY ==========")

    for source, destination in links:
        print(f"\nEnter telemetry for {source} - {destination}")

        measurements = {}

        for feature, label in FEATURES:
            maximum = 100 if feature in (
                "utilization_percent",
                "packet_loss_percent",
                "queue_occupancy_percent"
            ) else None

            measurements[feature] = read_float(
                f"{label}: ",
                minimum=0,
                maximum=maximum
            )

        telemetry[frozenset((source, destination))] = measurements

    return telemetry


def choose_endpoints(nodes):
    print("\nAvailable nodes:", ", ".join(nodes))

    while True:
        source = input("Source node: ").strip()
        destination = input("Destination node: ").strip()

        if source not in nodes or destination not in nodes:
            print("Please select existing nodes.")
        elif source == destination:
            print("Source and destination must be different.")
        else:
            return source, destination


def format_path(path):
    return " -> ".join(map(str, path)) if path else "No path found"


def show_results(result):
    print("\n========== ML CONGESTION PREDICTIONS ==========")

    for item in result["predictions"]:
        link = item["link"]

        if isinstance(link, (tuple, list, set, frozenset)):
            link = " - ".join(map(str, link))

        congestion = "YES" if item["prediction"] == 1 else "NO"

        print(f"\nLink: {link}")
        print("Congestion:", congestion)
        print(f"Original cost: {item['original_cost']:.2f}")
        print(f"Updated cost: {item['updated_cost']:.2f}")

    print("\n========== ROUTING COMPARISON ==========")

    print("\nConventional Dijkstra:")
    print("Path:", format_path(result["conventional_path"]))
    print(f"Cost: {result['conventional_cost']:.2f}")

    print("\nML-Assisted Adaptive Routing:")
    print("Path:", format_path(result["adaptive_path"]))
    print(f"Adjusted cost: {result['adaptive_cost']:.2f}")

    if not result["conventional_path"] or not result["adaptive_path"]:
        print("\nRESULT: No available route between the selected nodes.")

    elif result["route_changed"]:
        print("\nRESULT: Routing path changed due to congestion predictions.")

    else:
        print("\nRESULT: Routing path remained unchanged.")

    print("=" * 60)


def main():
    print("=" * 60)
    print("ADAPTINET - ML-ASSISTED ADAPTIVE ROUTING")
    print("=" * 60)

    while True:
        nodes = collect_nodes()

        network, links = collect_links(nodes)

        telemetry = collect_telemetry(links)

        alpha = read_float(
            "\nCongestion penalty (alpha): ",
            minimum=0
        )

        source, destination = choose_endpoints(nodes)

        try:
            result = run_adaptinet(
                network,
                telemetry,
                source,
                destination,
                alpha
            )

            show_results(result)

        except Exception as error:
            print("\nError:", error)

        again = input(
            "\nRun another experiment? (y/n): "
        ).strip().lower()

        if again != "y":
            print("\nExiting ADAPTINET.")
            break


if __name__ == "__main__":
    main()
