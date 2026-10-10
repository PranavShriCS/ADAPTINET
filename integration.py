
from app import predict_congestion
from routing.dijkstra import dijkstra
import csv
import os

network = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 2},
    "C": {"A": 3, "D": 3},
    "D": {"B": 2, "C": 3}
}

FEATURES = [
    "utilization_percent",
    "latency_ms",
    "packet_loss_percent",
    "throughput_mbps",
    "queue_occupancy_percent",
    "packet_arrival_rate_pps"
]

alpha = 6

# All values below are simulated test inputs.
scenarios = {
    "Normal Traffic": {
        "A-B": [20, 8, 0, 95, 10, 100],
        "B-D": [25, 10, 0, 90, 15, 150],
        "A-C": [20, 9, 0, 92, 12, 120],
        "C-D": [25, 10, 0, 90, 15, 150]
    },

    "Moderate Congestion": {
        "A-B": [30, 10, 0, 90, 20, 200],
        "B-D": [65, 40, 2, 65, 60, 600],
        "A-C": [20, 8, 0, 95, 10, 100],
        "C-D": [20, 8, 0, 95, 10, 100]
    },

    "Heavy Congestion": {
        "A-B": [30, 10, 0, 90, 20, 200],
        "B-D": [95, 100, 8, 30, 95, 1200],
        "A-C": [15, 5, 0, 98, 5, 80],
        "C-D": [15, 5, 0, 98, 5, 80]
    }
}


def test_scenario(name, telemetry):
    print("\n========================================")
    print("SCENARIO:", name)
    print("========================================")

    baseline_path, baseline_cost = dijkstra(
        network, "A", "D"
    )

    adaptive_network = {
        node: neighbours.copy()
        for node, neighbours in network.items()
    }

    link_results = []

    for link, values in telemetry.items():
        link_data = dict(zip(FEATURES, values))

        prediction, probability = predict_congestion(
            link_data
        )

        node1, node2 = link.split("-")

        original_cost = network[node1][node2]
        updated_cost = original_cost + alpha * probability

        adaptive_network[node1][node2] = updated_cost
        adaptive_network[node2][node1] = updated_cost

        print("\nLink:", link)
        print("Prediction:", prediction)
        print("Probability:", round(probability, 4))
        print("Original cost:", original_cost)
        print("Updated cost:", round(updated_cost, 4))

        link_results.append({
            "scenario": name,
            "link": link,
            "prediction": prediction,
            "probability": round(float(probability), 4),
            "original_cost": original_cost,
            "updated_cost": round(float(updated_cost), 4)
        })

    adaptive_path, adaptive_cost = dijkstra(
        adaptive_network, "A", "D"
    )

    print("\n----- ROUTING COMPARISON -----")
    print("Conventional path:", " -> ".join(baseline_path))
    print("Conventional cost:", baseline_cost)
    print("Adaptive path:", " -> ".join(adaptive_path))
    print("Adaptive cost:", round(adaptive_cost, 4))

    changed = baseline_path != adaptive_path

    print("Route changed:", "YES" if changed else "NO")

    summary = {
        "scenario": name,
        "baseline_path": " -> ".join(baseline_path),
        "baseline_cost": baseline_cost,
        "adaptive_path": " -> ".join(adaptive_path),
        "adaptive_cost": round(float(adaptive_cost), 4),
        "route_changed": "YES" if changed else "NO"
    }

    return summary, link_results


os.makedirs("results", exist_ok=True)

summary_results = []
all_link_results = []

for name, telemetry in scenarios.items():
    summary, links = test_scenario(name, telemetry)

    summary_results.append(summary)
    all_link_results.extend(links)


with open(
    "results/scenario_summary.csv",
    "w",
    newline=""
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=summary_results[0].keys()
    )
    writer.writeheader()
    writer.writerows(summary_results)


with open(
    "results/link_predictions.csv",
    "w",
    newline=""
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=all_link_results[0].keys()
    )
    writer.writeheader()
    writer.writerows(all_link_results)


print("\n========================================")
print("FINAL SCENARIO SUMMARY")
print("========================================")

for result in summary_results:
    print("\nScenario:", result["scenario"])
    print("Baseline:", result["baseline_path"])
    print("Adaptive:", result["adaptive_path"])
    print("Route changed:", result["route_changed"])

print("\nResults saved in results/ folder")
