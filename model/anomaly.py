from sklearn.ensemble import IsolationForest
import numpy as np

X = np.random.rand(500,3)

model = IsolationForest(
    contamination=0.08,
    random_state=42
)

model.fit(X)

def detect_anomaly(
    amount,
    hour,
    location_change
):
    sample = [[
        amount/50000,
        hour/24,
        location_change
    ]]

    pred = model.predict(sample)

    return pred[0] == -1