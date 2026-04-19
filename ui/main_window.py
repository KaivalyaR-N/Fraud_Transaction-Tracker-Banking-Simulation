from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from model.predict import predict_transaction
from simulator.transaction_gen import generate_transaction


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("💳 Fraud Analytics Dashboard")
        self.setGeometry(100, 100, 800, 500)

        main_layout = QHBoxLayout()

        # LEFT SIDE (Table + Alerts)
        left_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Amount", "Hour", "Location", "Result"])
        left_layout.addWidget(self.table)

        self.alert_label = QLabel("🚨 Alerts: None")
        left_layout.addWidget(self.alert_label)

        main_layout.addLayout(left_layout)

        # RIGHT SIDE (Graph)
        right_layout = QVBoxLayout()

        self.graph = pg.PlotWidget()
        self.graph.setTitle("Fraud Detection Trend")
        right_layout.addWidget(self.graph)

        self.x = []
        self.y = []

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_transaction)
        self.timer.start(1000)

    def run_transaction(self):
        txn = generate_transaction()

        result = predict_transaction(
            txn["amount"],
            txn["hour"],
            txn["location_change"]
        )

        # Add to table
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(txn["amount"])))
        self.table.setItem(row, 1, QTableWidgetItem(str(txn["hour"])))
        self.table.setItem(row, 2, QTableWidgetItem(str(txn["location_change"])))
        self.table.setItem(row, 3, QTableWidgetItem(result))

        # Alert update
        if "Fraud" in result:
            self.alert_label.setText(f"🚨 Fraud detected: ₹{txn['amount']}")

        # Graph update
        self.x.append(len(self.x))
        self.y.append(1 if "Fraud" in result else 0)

        self.graph.plot(self.x, self.y, clear=True)