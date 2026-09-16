import numpy as np
import pandas as pd #to read the csv file
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler

pd.read_excel("/content/ADAPTINET_synthetic_network_dataset.csv")

train,valid ,test = np.split(df.sample(frac=1),[int(0.6*len(df)),int(0.8*len(df))])

def scale_dataset(dataframe, oversample=False):
  x=dataframe[dataframe.columns[:-2]].values#first few rows (2D vector)
  y=dataframe[dataframe.columns[-2]].values#last row (1D vector)

  scaler=StandardScaler()
  x=scaler.fit_transform(x)
  #
  if oversample:
    ros=RandomOverSampler()
    x,y=ros.fit_resample(x,y)

  data=np.hstack((x,np.reshape(y,(-1,1))))

  return data,x,y

train , x_train , y_train = scale_dataset(train,oversample=True)
valid , x_valid , y_valid = scale_dataset(valid,oversample=False)
test , x_test , y_test = scale_dataset(test,oversample=False)

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

models = {

    "Decision Tree": DecisionTreeClassifier(
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),

    "XGBoost": XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
}


# --------------------------------------------------
# 5. TRAIN + EVALUATE EACH MODEL
# --------------------------------------------------

results = []

for name, model in models.items():

    print("\n===================================")
    print(name)
    print("===================================")

    # Train
    model.fit(x_train, y_train)

    # Prediction
    y_pred = model.predict(x_test)

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # Store results
    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    # Print metrics
    print("Accuracy :", accuracy)
    print("Precision:", precision)
    print("Recall   :", recall)
    print("F1 Score :", f1)

    # Confusion Matrix
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Detailed report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))


# --------------------------------------------------
# 6. COMPARE ALL MODELS
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n\n========== MODEL COMPARISON ==========")
print(results_df.to_string(index=False))


# --------------------------------------------------
# 7. FIND BEST MODEL
# --------------------------------------------------

best_model = results_df.loc[
    results_df["F1 Score"].idxmax()
]

print("\n========== BEST MODEL ==========")

print("Model    :", best_model["Model"])
print("Accuracy :", best_model["Accuracy"])
print("Precision:", best_model["Precision"])
print("Recall   :", best_model["Recall"])
print("F1 Score :", best_model["F1 Score"])


# --------------------------------------------------
# 8. CONGESTION PROBABILITY
# --------------------------------------------------

print("\n========== CONGESTION PROBABILITY ==========")

# Example network link
sample_link = pd.DataFrame([{
    "utilization_percent": 90,
    "latency_ms": 80,
    "packet_loss_percent": 5,
    "throughput_mbps": 50,
    "queue_occupancy_percent": 85,
    "packet_arrival_rate_pps": 900
}])

# Use XGBoost here as an example
xgb_model = models["XGBoost"]

probability = xgb_model.predict_proba(sample_link)[0][1]

print("Probability of congestion:", probability)