def predict_transaction(amount, hour, location_change):
    data = [[amount, hour, location_change]]
    result = model.predict(data)[0]

    # 🔥 rule override (real logic)
    if amount > 20000 and location_change == 1:
        return "🚨 Fraud"

    return "🚨 Fraud" if result == 1 else "✅ Legit"