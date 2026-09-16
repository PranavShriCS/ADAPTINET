# ADAPTINET - Dynamic Cost Routing

network = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 2},
    "C": {"A": 3, "D": 3},
    "D": {"B": 2, "C": 3}
}


def dijkstra(network, start, destination):
    distances = {}
    previous = {}
    unvisited = set(network.keys())

    for node in network:
        distances[node] = float("inf")
        previous[node] = None

    distances[start] = 0

    while unvisited:
        current = min(
            unvisited,
            key=lambda node: distances[node]
        )

        if distances[current] == float("inf"):
            break

        unvisited.remove(current)

        for neighbour, cost in network[current].items():
            new_distance = distances[current] + cost

            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                previous[neighbour] = current

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path, distances[destination]


# Normal network
path, cost = dijkstra(network, "A", "D")

print("Normal network:")
print("Shortest path:", " -> ".join(path))
print("Total cost:", cost)


# Congested network
congested_network = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 8},
    "C": {"A": 3, "D": 3},
    "D": {"B": 8, "C": 3}
}

path, cost = dijkstra(congested_network, "A", "D")

print("\nAfter B-D congestion:")
print("Shortest path:", " -> ".join(path))
print("Total cost:", cost)