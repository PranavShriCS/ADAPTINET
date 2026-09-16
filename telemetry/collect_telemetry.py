# ADAPTINET - Network Telemetry Collection

import csv


links = {
    "A-B": {
        "utilization": 0.30,
        "latency": 10,
        "packet_loss": 0.00,
        "throughput": 90
    },
    "B-D": {
        "utilization": 0.85,
        "latency": 45,
        "packet_loss": 0.03,
        "throughput": 70
    },
    "A-C": {
        "utilization": 0.25,
        "latency": 12,
        "packet_loss": 0.00,
        "throughput": 88
    },
    "C-D": {
        "utilization": 0.40,
        "latency": 18,
        "packet_loss": 0.01,
        "throughput": 80
    }
}


def collect_telemetry(links):
    telemetry = []

    for link, metrics in links.items():
        telemetry.append({
            "link": link,
            "utilization": metrics["utilization"],
            "latency": metrics["latency"],
            "packet_loss": metrics["packet_loss"],
            "throughput": metrics["throughput"]
        })

    return telemetry


def save_telemetry(telemetry, filename):
    with open(filename, "w", newline="") as file:
        fieldnames = [
            "link",
            "utilization",
            "latency",
            "packet_loss",
            "throughput"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(telemetry)


telemetry = collect_telemetry(links)

save_telemetry(
    telemetry,
    "../data/telemetry.csv"
)

print("Telemetry collected successfully")
print("Link, Utilization, Latency, Packet Loss, Throughput")

for entry in telemetry:
    print(
        f"{entry['link']}, "
        f"{entry['utilization']}, "
        f"{entry['latency']}, "
        f"{entry['packet_loss']}, "
        f"{entry['throughput']}"
    )