
from app import predict_congestion
from routing.dijkstra import dijkstra

# Original network costs
network = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 2},
    "C": {"A": 3, "D": 3},
    "D": {"B": 2, "C": 3}
}

# Simulated link telemetry
telemetry = {
    "A-B": [30, 10, 0, 90, 20, 200],
    "B-D": [90, 80, 5, 50, 85, 900],
    "A-C": [25, 12, 0, 88, 15, 180],
    "C-D": [40, 18, 1, 80, 30, 300]
}

alpha = 6

print("\n========== ADAPTINET INTEGRATION ==========")

# Conventional shortest path
normal_path, normal_cost = dijkstra(network, "A", "D")

print("\nConventional Routing")
print("Path:", " -> ".join(normal_path))
print("Cost:", normal_cost)

# Adjust costs using ML predictions
adaptive_network = {
    node: neighbours.copy()
    for node, neighbours in network.items()
}

for link, values in telemetry.items():

    link_data = {
        "utilization_percent": values[0],
        "latency_ms": values[1],
        "packet_loss_percent": values[2],
        "throughput_mbps": values[3],
        "queue_occupancy_percent": values[4],
        "packet_arrival_rate_pps": values[5]
    }

    prediction, probability = predict_congestion(link_data)

    node1, node2 = link.split("-")

    original_cost = network[node1][node2]
    updated_cost = original_cost + alpha * probability

    adaptive_network[node1][node2] = updated_cost
    adaptive_network[node2][node1] = updated_cost

    print(f"\nLink: {link}")
    print(f"Congestion prediction: {prediction}")
    print(f"Congestion probability: {probability:.4f}")
    print(f"Original cost: {original_cost}")
    print(f"Updated cost: {updated_cost:.4f}")

# Adaptive shortest path
adaptive_path, adaptive_cost = dijkstra(
    adaptive_network, "A", "D"
)

print("\n========== ROUTING COMPARISON ==========")

print("\nConventional routing:")
print("Path:", " -> ".join(normal_path))
print("Cost:", normal_cost)

print("\nAI-assisted adaptive routing:")
print("Path:", " -> ".join(adaptive_path))
print("Adjusted cost:", round(adaptive_cost, 4))

if normal_path != adaptive_path:
    print("\nRESULT: Routing path changed due to ML-based costs")
else:
    print("\nRESULT: Routing path remained unchanged")
