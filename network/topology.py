# ADAPTINET - Initial Network Topology

network = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 2},
    "C": {"A": 3, "D": 3},
    "D": {"B": 2, "C": 3}
}

print("Network created successfully")
print()

print("Nodes:")
print("A B C D")
print()

print("Links:")

for node in network:
    for neighbour, cost in network[node].items():
        if node < neighbour:
            print(f"{node}-{neighbour} : {cost}")