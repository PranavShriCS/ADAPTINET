
import math

from routing.engine import run_adaptinet, FEATURES


def get_number(prompt, minimum=0, maximum=None):
    while True:
        try:
            value = float(input(prompt))

            if not math.isfinite(value):
                raise ValueError

            if value < minimum:
                raise ValueError

            if maximum is not None and value > maximum:
                raise ValueError

            return value

        except ValueError:
            print("Invalid number. Please try again.")


def get_integer(prompt, minimum=1, maximum=None):
    while True:
        value = get_number(prompt, minimum, maximum)

        if value.is_integer():
            return int(value)

        print("Please enter a whole number.")


def get_node(prompt, network):
    while True:
        node = input(prompt).strip().upper()

        if node in network:
            return node

        print("Invalid node. Available nodes:",
              ", ".join(network))


def create_network():
    print("\n========== NETWORK CONFIGURATION ==========")

    node_count = get_integer(
        "Enter number of nodes: ",
        minimum=2
    )

    network = {}

    for i in range(node_count):
        while True:
            node = input(
                f"Enter name of node {i + 1}: "
            ).strip().upper()

            if not node:
                print("Node name cannot be empty.")
                continue

            if node in network:
                print("Node already exists.")
                continue

            network[node] = {}
            break

    maximum_links = node_count * (node_count - 1) // 2

    link_count = get_integer(
        "Enter number of links: ",
        minimum=1,
        maximum=maximum_links
    )

    links = []

    for i in range(link_count):
        print(f"\n----- Link {i + 1} -----")

        while True:
            node1 = get_node("First node: ", network)
            node2 = get_node("Second node: ", network)

            if node1 == node2:
                print("A link must connect two different nodes.")
                continue

            if node2 in network[node1]:
                print("This link already exists.")
                continue

            break

        cost = get_number(
            "Enter original link cost: ",
            minimum=0
        )

        network[node1][node2] = cost
        network[node2][node1] = cost

        links.append((node1, node2))

    return network, links


def collect_telemetry(links):
    print("\n========== TELEMETRY INPUT ==========")

    telemetry = {}

    percentage_features = {
        "utilization_percent",
        "packet_loss_percent",
        "queue_occupancy_percent"
    }

    for node1, node2 in links:
        print(f"\n----- Link {node1} <-> {node2} -----")

        values = {}

        for feature in FEATURES:
            maximum = (
                100 if feature in percentage_features else None
            )

            values[feature] = get_number(
                f"Enter {feature}: ",
                minimum=0,
                maximum=maximum
            )

        telemetry[frozenset((node1, node2))] = values

    return telemetry


def show_results(results):
    print("\n========== ML CONGESTION PREDICTIONS ==========")

    for item in results["predictions"]:
        print("\nLink:", item["link"])
        print("Congestion prediction:", item["prediction"])
        print(
            "Congestion probability:",
            round(item["probability"], 4)
        )
        print("Original cost:", item["original_cost"])
        print(
            "Updated cost:",
            round(item["updated_cost"], 4)
        )

    print("\n========== ROUTING COMPARISON ==========")

    conventional_path = results["conventional_path"]
    adaptive_path = results["adaptive_path"]

    if not conventional_path or not adaptive_path:
        print("No route exists between the selected nodes.")
        return

    print("\nConventional routing:")
    print("Path:", " -> ".join(conventional_path))
    print("Cost:", results["conventional_cost"])

    print("\nAI-assisted adaptive routing:")
    print("Path:", " -> ".join(adaptive_path))
    print(
        "Adjusted cost:",
        round(results["adaptive_cost"], 4)
    )

    if results["route_changed"]:
        print("\nRESULT: Routing path changed")
    else:
        print("\nRESULT: Routing path remained unchanged")


def main():
    while True:
        print("\n======================================")
        print("             ADAPTINET")
        print(" AI-Based Adaptive Network Routing")
        print("======================================")

        network, links = create_network()
        telemetry = collect_telemetry(links)

        alpha = get_number(
            "\nEnter congestion penalty coefficient: ",
            minimum=0
        )

        print("\nAvailable nodes:", ", ".join(network))

        source = get_node("Enter source node: ", network)

        while True:
            destination = get_node(
                "Enter destination node: ",
                network
            )

            if destination != source:
                break

            print("Source and destination must be different.")

        try:
            results = run_adaptinet(
                network,
                telemetry,
                source,
                destination,
                alpha
            )

            show_results(results)

        except ValueError as error:
            print("\nError:", error)

        again = input(
            "\nRun another experiment? (y/n): "
        ).strip().lower()

        if again != "y":
            print("\nExiting ADAPTINET.")
            break


if __name__ == "__main__":
    main()
