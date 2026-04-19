import random

def generate_transaction():
    amount = random.randint(100, 50000)
    hour = random.randint(0, 23)
    
    # 20% chance of suspicious location change
    location_change = 1 if random.random() < 0.2 else 0

    return {
        "amount": amount,
        "hour": hour,
        "location_change": location_change
    }