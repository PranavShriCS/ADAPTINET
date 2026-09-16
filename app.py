import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


DATA_FILE = "ADAPTINET_synthetic_network_dataset.xlsx"

FEATURE_COLUMNS = [
    "utilization_percent",
    "latency_ms",
    "packet_loss_percent",
    "throughput_mbps",
    "queue_occupancy_percent",
    "packet_arrival_rate_pps"
]

TARGET_COLUMN = "congested"


df = pd.read_excel(DATA_FILE)

X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]

print("Dataset loaded successfully")
print("Dataset shape:", df.shape)
print("Features:", FEATURE_COLUMNS)
print("Target:", TARGET_COLUMN)

print("\nClass distribution:")
print(y.value_counts())


X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.40,
    random_state=42,
    stratify=y
)

X_valid, X_test, y_valid, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)


print("\nDataset split:")
print("Training:", X_train.shape)
print("Validation:", X_valid.shape)
print("Testing:", X_test.shape)


scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_valid_scaled = scaler.transform(X_valid)
X_test_scaled = scaler.transform(X_test)


ros = RandomOverSampler(random_state=42)

X_train_resampled, y_train_resampled = ros.fit_resample(
    X_train_scaled,
    y_train
)

print("\nTraining data after oversampling:")
print(pd.Series(y_train_resampled).value_counts())


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


results = []


for name, model in models.items():

    print("\n===================================")
    print(name)
    print("===================================")

    model.fit(
        X_train_resampled,
        y_train_resampled
    )

    y_valid_pred = model.predict(X_valid_scaled)

    accuracy = accuracy_score(y_valid, y_valid_pred)
    precision = precision_score(
        y_valid,
        y_valid_pred,
        zero_division=0
    )
    recall = recall_score(
        y_valid,
        y_valid_pred,
        zero_division=0
    )
    f1 = f1_score(
        y_valid,
        y_valid_pred,
        zero_division=0
    )

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    print("Validation Accuracy :", accuracy)
    print("Validation Precision:", precision)
    print("Validation Recall   :", recall)
    print("Validation F1 Score :", f1)

    print("\nValidation Confusion Matrix:")
    print(confusion_matrix(y_valid, y_valid_pred))

    print("\nValidation Classification Report:")
    print(
        classification_report(
            y_valid,
            y_valid_pred,
            zero_division=0
        )
    )


results_df = pd.DataFrame(results)

print("\n\n========== MODEL COMPARISON ==========")
print(results_df.to_string(index=False))


best_model_name = results_df.loc[
    results_df["F1 Score"].idxmax(),
    "Model"
]

print("\n========== SELECTED MODEL ==========")
print("Model:", best_model_name)


X_train_valid = pd.concat(
    [X_train, X_valid]
)

y_train_valid = pd.concat(
    [y_train, y_valid]
)


final_scaler = StandardScaler()

X_train_valid_scaled = final_scaler.fit_transform(
    X_train_valid
)

X_test_final_scaled = final_scaler.transform(
    X_test
)


final_ros = RandomOverSampler(
    random_state=42
)

X_train_valid_resampled, y_train_valid_resampled = final_ros.fit_resample(
    X_train_valid_scaled,
    y_train_valid
)


final_model = models[best_model_name]

final_model.fit(
    X_train_valid_resampled,
    y_train_valid_resampled
)


y_test_pred = final_model.predict(
    X_test_final_scaled
)


test_accuracy = accuracy_score(
    y_test,
    y_test_pred
)

test_precision = precision_score(
    y_test,
    y_test_pred,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    y_test_pred,
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    y_test_pred,
    zero_division=0
)


print("\n========== FINAL TEST RESULTS ==========")

print("Accuracy :", test_accuracy)
print("Precision:", test_precision)
print("Recall   :", test_recall)
print("F1 Score :", test_f1)

print("\nTest Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_test_pred
    )
)

print("\nTest Classification Report:")
print(
    classification_report(
        y_test,
        y_test_pred,
        zero_division=0
    )
)


def predict_congestion(link_data):

    link_df = pd.DataFrame([link_data])

    link_features = link_df[FEATURE_COLUMNS]

    link_scaled = final_scaler.transform(
        link_features
    )

    probability = final_model.predict_proba(
        link_scaled
    )[0][1]

    prediction = int(
        probability >= 0.5
    )

    return prediction, probability


sample_link = {
    "utilization_percent": 90,
    "latency_ms": 80,
    "packet_loss_percent": 5,
    "throughput_mbps": 50,
    "queue_occupancy_percent": 85,
    "packet_arrival_rate_pps": 900
}


prediction, probability = predict_congestion(
    sample_link
)

print("\n========== CONGESTION PREDICTION ==========")

print("Predicted congestion:", prediction)
print("Probability of congestion:", probability)


def predict_congestion(link_data):

    link_df = pd.DataFrame([link_data])

    link_features = link_df[FEATURE_COLUMNS]

    link_scaled = scaler.transform(
        link_features
    )

    probability = final_model.predict_proba(
        link_scaled
    )[0][1]

    prediction = int(
        probability >= 0.5
    )

    return prediction, probability


sample_link = {
    "utilization_percent": 90,
    "latency_ms": 80,
    "packet_loss_percent": 5,
    "throughput_mbps": 50,
    "queue_occupancy_percent": 85,
    "packet_arrival_rate_pps": 900
}


prediction, probability = predict_congestion(
    sample_link
)

print("\n========== CONGESTION PREDICTION ==========")

print("Predicted congestion:", prediction)
print("Probability of congestion:", probability)