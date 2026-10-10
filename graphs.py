
import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("graphs", exist_ok=True)

summary = pd.read_csv("results/scenario_summary.csv")
links = pd.read_csv("results/link_predictions.csv")

# GRAPH 1: ML MODEL COMPARISON

models = ["Decision Tree", "Random Forest", "XGBoost"]
accuracy = [0.8200, 0.8225, 0.8200]
f1_scores = [0.819095, 0.814621, 0.813472]

x = range(len(models))
width = 0.35

plt.figure(figsize=(9, 5))
plt.bar(
    [i - width / 2 for i in x],
    accuracy,
    width,
    label="Validation Accuracy"
)
plt.bar(
    [i + width / 2 for i in x],
    f1_scores,
    width,
    label="Validation F1 Score"
)

plt.xticks(list(x), models)
plt.ylim(0, 1)
plt.ylabel("Score")
plt.title("ML Model Performance Comparison")
plt.legend()
plt.tight_layout()
plt.savefig("graphs/model_comparison.png", dpi=300)
plt.close()


# GRAPH 2: CONGESTION PREDICTIONS

prediction_table = links.pivot(
    index="link",
    columns="scenario",
    values="prediction"
)

prediction_table = prediction_table.reindex(
    columns=summary["scenario"].tolist()
)

prediction_table.plot(
    kind="bar",
    figsize=(10, 5)
)

plt.title("Predicted Congestion Across Traffic Scenarios")
plt.xlabel("Network Link")
plt.ylabel("Congestion Prediction (0 or 1)")
plt.yticks([0, 1])
plt.xticks(rotation=0)
plt.legend(title="Scenario")
plt.tight_layout()
plt.savefig("graphs/congestion_predictions.png", dpi=300)
plt.close()


# GRAPH 3: LINK COST COMPARISON

for scenario in summary["scenario"]:
    data = links[links["scenario"] == scenario]

    x = range(len(data))
    width = 0.35

    plt.figure(figsize=(9, 5))

    plt.bar(
        [i - width / 2 for i in x],
        data["original_cost"],
        width,
        label="Original Cost"
    )

    plt.bar(
        [i + width / 2 for i in x],
        data["updated_cost"],
        width,
        label="ML-Adjusted Cost"
    )

    plt.xticks(list(x), data["link"])
    plt.xlabel("Network Link")
    plt.ylabel("Routing Cost")
    plt.title(f"Link Cost Comparison - {scenario}")
    plt.legend()
    plt.tight_layout()

    filename = scenario.lower().replace(" ", "_")
    plt.savefig(
        f"graphs/link_costs_{filename}.png",
        dpi=300
    )
    plt.close()


# GRAPH 4: ROUTING PATH COMPARISON

fig, ax = plt.subplots(figsize=(10, 5))

y = range(len(summary))

ax.scatter(
    summary["baseline_path"],
    [i - 0.12 for i in y],
    s=140,
    marker="o",
    label="Conventional Routing"
)

ax.scatter(
    summary["adaptive_path"],
    [i + 0.12 for i in y],
    s=140,
    marker="s",
    label="AI-Assisted Routing"
)

ax.set_yticks(list(y))
ax.set_yticklabels(summary["scenario"])
ax.set_xlabel("Selected Route")
ax.set_title("Conventional vs AI-Assisted Route Selection")
ax.legend()
ax.grid(axis="x", alpha=0.25)

plt.tight_layout()
plt.savefig("graphs/routing_comparison.png", dpi=300)
plt.close()


print("\nAll graphs generated successfully!")
print("Check the graphs folder.")
