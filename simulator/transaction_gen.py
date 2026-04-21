import random
import time

def generate_transaction():
    current_hour = time.localtime().tm_hour

    amount = random.choice([
        random.randint(100, 2000),      # normal
        random.randint(2000, 10000),    # medium
        random.randint(10000, 50000)    # risky
    ])

    # realistic fraud patterns
    location_change = 1 if random.random() < 0.15 else 0

    # night transactions more suspicious
    if current_hour < 6 or current_hour > 23:
        location_change = 1 if random.random() < 0.4 else 0

    return {
        "amount": amount,
        "hour": current_hour,
        "location_change": location_change
    }