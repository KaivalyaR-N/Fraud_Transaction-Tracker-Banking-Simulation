from model.predict import predict_transaction
from simulator.transaction_gen import generate_transaction
import time
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

print("💳 Live Transaction Monitoring Started...\n")
app = QApplication(sys.argv)

window = MainWindow()
window.show()
for i in range(10):  # 10 transactions simulate
    txn = generate_transaction()

    result = predict_transaction(
        txn["amount"],
        txn["hour"],
        txn["location_change"]
    )

    print(f"Transaction {i+1}:")
    print(f"Amount: ₹{txn['amount']}")
    print(f"Hour: {txn['hour']}")
    print(f"Location Change: {txn['location_change']}")
    print(f"Result: {result}")
    print("-" * 30)

    sys.exit(app.exec_())

    time.sleep(1)  # delay for realism