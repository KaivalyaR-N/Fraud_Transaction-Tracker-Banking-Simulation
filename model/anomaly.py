from sklearn.ensemble import IsolationForest
import numpy as np

# 🔥 More realistic baseline:
# mostly normal transactions
amounts = np.random.uniform(0.01, 0.20, 500)      # normalized
hours = np.random.uniform(0.25, 0.90, 500)        # daytime bias
locations = np.random.choice([0,1], 500, p=[0.95,0.05])

X = np.column_stack(
    (amounts, hours, locations)
)

# VERY LOW anomaly rate
model = IsolationForest(
    contamination=0.02,   # was too high before
    random_state=42
)

model.fit(X)


def detect_anomaly(
    amount,
    hour,
    location_change
):
    # normalize
    a = amount / 50000
    h = hour / 24

    # Hard-rule anomalies (rare serious cases only)
    if amount > 40000 and location_change == 1:
        return True

    if amount > 30000 and (hour < 5 or hour > 23):
        return True

    # ML anomaly check
    sample = [[a, h, location_change]]

    pred = model.predict(sample)

    return pred[0] == -1