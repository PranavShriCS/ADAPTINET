
import math

from app import predict_congestion
from routing.dijkstra import dijkstra


FEATURES = [
    "utilization_percent",
    "latency_ms",
    "packet_loss_percent",
    "throughput_mbps",
    "queue_occupancy_percent",
    "packet_arrival_rate_pps"
]


def run_adaptinet(network, telemetry, source, destination, alpha):
    if source not in network or destination not in network:
        raise ValueError("Invalid source or destination node.")

    if source == destination:
        raise ValueError("Source and destination must be different.")

    if not math.isfinite(alpha) or alpha < 0:
        raise ValueError("Congestion penalty must be non-negative.")

    adaptive_network = {
        node: neighbours.copy()
        for node, neighbours in network.items()
    }

    predictions = []

    for node, neighbours in network.items():
        for neighbour, cost in neighbours.items():
            if neighbour not in network:
                raise ValueError("Link references an unknown node.")

            if not math.isfinite(cost) or cost < 0:
                raise ValueError("Link costs must be non-negative.")

            if node not in network[neighbour]:
                raise ValueError("Network links must be bidirectional.")

            if network[neighbour][node] != cost:
                raise ValueError("Link costs must match in both directions.")

    processed = set()

    for node1, neighbours in network.items():
        for node2, original_cost in neighbours.items():
            link_key = frozenset((node1, node2))

            if link_key in processed:
                continue

            processed.add(link_key)

            if link_key not in telemetry:
                raise ValueError(
                    f"Missing telemetry for link {node1}-{node2}."
                )

            values = telemetry[link_key]

            if set(values.keys()) != set(FEATURES):
                raise ValueError(
                    f"Incorrect telemetry features for {node1}-{node2}."
                )

            for feature, value in values.items():
                if not math.isfinite(value) or value < 0:
                    raise ValueError(
                        f"Invalid value for {feature}."
                    )

                if feature in (
                    "utilization_percent",
                    "packet_loss_percent",
                    "queue_occupancy_percent"
                ) and value > 100:
                    raise ValueError(
                        f"{feature} cannot exceed 100."
                    )

            prediction, probability = predict_congestion(values)

            updated_cost = original_cost + alpha * probability

            adaptive_network[node1][node2] = updated_cost
            adaptive_network[node2][node1] = updated_cost

            predictions.append({
                "link": f"{node1}-{node2}",
                "prediction": int(prediction),
                "probability": float(probability),
                "original_cost": original_cost,
                "updated_cost": updated_cost
            })

    conventional_path, conventional_cost = dijkstra(
        network, source, destination
    )

    adaptive_path, adaptive_cost = dijkstra(
        adaptive_network, source, destination
    )

    return {
        "predictions": predictions,
        "conventional_path": conventional_path,
        "conventional_cost": conventional_cost,
        "adaptive_path": adaptive_path,
        "adaptive_cost": adaptive_cost,
        "route_changed": conventional_path != adaptive_path
    }
