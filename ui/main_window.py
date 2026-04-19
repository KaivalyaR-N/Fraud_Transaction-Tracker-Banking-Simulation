from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QFrame
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from model.predict import predict_transaction
from simulator.transaction_gen import generate_transaction


class GlassCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 10px;
            }
        """)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("💳 Fraud Analytics Pro")
        self.setGeometry(100, 100, 1000, 600)

        # 🌌 Background
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: white;
                font-family: Arial;
            }
        """)

        main_layout = QHBoxLayout()

        # 🔹 LEFT PANEL
        left_panel = QVBoxLayout()

        self.table_card = GlassCard()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Amount", "Hour", "Location", "Result"])
        self.table.setStyleSheet("background: transparent;")

        table_layout.addWidget(QLabel("📋 Transactions"))
        table_layout.addWidget(self.table)

        self.table_card.setLayout(table_layout)
        left_panel.addWidget(self.table_card)

        # 🔹 ALERT CARD
        self.alert_card = GlassCard()
        alert_layout = QVBoxLayout()

        self.alert_label = QLabel("🚨 No Alerts")
        self.alert_label.setStyleSheet("font-size: 16px;")

        alert_layout.addWidget(QLabel("⚠️ Alerts"))
        alert_layout.addWidget(self.alert_label)

        self.alert_card.setLayout(alert_layout)
        left_panel.addWidget(self.alert_card)

        main_layout.addLayout(left_panel)

        # 🔹 RIGHT PANEL (GRAPH)
        right_panel = QVBoxLayout()

        self.graph_card = GlassCard()
        graph_layout = QVBoxLayout()

        self.graph = pg.PlotWidget()
        self.graph.setBackground(None)

        graph_layout.addWidget(QLabel("📊 Fraud Trend"))
        graph_layout.addWidget(self.graph)

        self.graph_card.setLayout(graph_layout)
        right_panel.addWidget(self.graph_card)

        main_layout.addLayout(right_panel)

        self.setLayout(main_layout)

        # 📊 Graph data
        self.x = []
        self.y = []

        # ⏱ Timer
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

        # Table update
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(f"₹{txn['amount']}"))
        self.table.setItem(row, 1, QTableWidgetItem(str(txn["hour"])))
        self.table.setItem(row, 2, QTableWidgetItem(str(txn["location_change"])))
        self.table.setItem(row, 3, QTableWidgetItem(result))

        # Alert update
        if "Fraud" in result:
            self.alert_label.setText(f"🚨 Fraud: ₹{txn['amount']}")
            self.alert_label.setStyleSheet("color: red; font-size: 16px;")
        else:
            self.alert_label.setText("✅ System Normal")
            self.alert_label.setStyleSheet("color: lightgreen; font-size: 16px;")

        # Graph update
        self.x.append(len(self.x))
        self.y.append(1 if "Fraud" in result else 0)

        self.graph.plot(self.x, self.y, clear=True, pen='r')