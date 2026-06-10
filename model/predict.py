import pickle
import pandas as pd

import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "saved_model.pkl"
)

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


def predict_transaction(amount, hour, location_change):
    # convert into dataframe (important)
    data = pd.DataFrame([[amount, hour, location_change]],
                        columns=["amount", "hour", "location_change"])

    prediction = model.predict(data)[0]

    # return clean label
    return "Fraud" if prediction == 1 else "Legit"