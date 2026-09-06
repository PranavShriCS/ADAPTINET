# ADAPTINET - Traffic Simulation

import random

nodes = ["A", "B", "C", "D"]

traffic_requests = []

for i in range(5):
    source = random.choice(nodes)
    destination = random.choice(nodes)

    while destination == source:
        destination = random.choice(nodes)

    traffic = random.randint(1, 10)

    traffic_requests.append({
        "source": source,
        "destination": destination,
        "traffic": traffic
    })


# Network links
link_load = {
    "A-B": 0,
    "A-C": 0,
    "B-D": 0,
    "C-D": 0
}


print("Traffic simulation started")
print()

for request in traffic_requests:
    print(
        f"{request['source']} -> {request['destination']} : "
        f"{request['traffic']} units"
    )

print()
print("Link loads:")

for link, load in link_load.items():
    print(f"{link} : {load} units")