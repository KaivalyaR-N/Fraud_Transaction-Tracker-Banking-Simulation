import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

# Dummy dataset
np.random.seed(42)

data = {
    "amount": np.random.randint(100, 50000, 500),
    "hour": np.random.randint(0, 24, 500),
    "location_change": np.random.randint(0, 2, 500),
    "is_fraud": np.random.randint(0, 2, 500)
}

df = pd.DataFrame(data)

# Features & target
X = df[["amount", "hour", "location_change"]]
y = df["is_fraud"]

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
with open("model/saved_model.pkl", "wb") as f:
    pickle.dump(model, f)

print(" Model trained and saved!")