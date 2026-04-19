import pickle

# Load model
with open("model/saved_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict_transaction(amount, hour, location_change):
    data = [[amount, hour, location_change]]
    result = model.predict(data)[0]

    if result == 1:
        return "🚨 Fraud"
    else:
        return "✅ Legit"