import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Sample training dataset (simulated, standards-based)
data = {
    "ph": [7.2, 6.8, 8.0, 5.9, 9.1, 7.4, 6.3, 8.7],
    "turbidity": [2.1, 3.5, 4.0, 12.0, 8.5, 1.5, 6.0, 11.2],
    "temperature": [25, 26, 24, 32, 35, 22, 29, 31],
    "label": ["Safe", "Safe", "Safe", "Unsafe", "Unsafe", "Safe", "Unsafe", "Unsafe"]
}

df = pd.DataFrame(data)

X = df[["ph", "turbidity", "temperature"]]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

joblib.dump(model, "model.pkl")
print("Model saved as model.pkl")
