import pickle
import pandas as pd

# 🔥 LOAD MODEL ONCE
with open("model/saved_model.pkl", "rb") as f:
    model = pickle.load(f)


def predict_transaction(amount, hour, location_change):
    # convert into dataframe (important)
    data = pd.DataFrame([[amount, hour, location_change]],
                        columns=["amount", "hour", "location_change"])

    prediction = model.predict(data)[0]

    # return clean label
    return "Fraud" if prediction == 1 else "Legit"