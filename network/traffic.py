# ADAPTINET - Traffic Simulation

# Simulate traffic travelling through A -> B -> D

traffic_levels = {
    "Normal": 10,
    "Medium": 50,
    "Heavy": 100
}

print("Traffic simulation started")
print()

for level, traffic in traffic_levels.items():
    print(f"{level} traffic:")
    print(f"A -> B -> D : {traffic} units")
    print(f"B-D link load: {traffic} units")
    print()