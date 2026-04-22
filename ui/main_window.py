from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QFrame, QListWidget, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QColor
from PyQt5.QtMultimedia import QSoundEffect

import pyqtgraph as pg
import csv
import os

from model.predict import predict_transaction
from model.anomaly import detect_anomaly
from simulator.transaction_gen import generate_transaction


class GlassCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 10px;
            }
        """)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("💳 Fraud Analytics Pro")
        self.showMaximized()

        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: white;
                font-family: Arial;
            }
        """)

        # KPI
        self.fraud_total = 0
        self.legit_total = 0

        kpi_layout = QHBoxLayout()

        self.fraud_card = QLabel("🚨 Fraud: 0")
        self.legit_card = QLabel("✅ Legit: 0")
        self.risk_card = QLabel("⚠️ Risk: 0%")

        for card in [self.fraud_card, self.legit_card, self.risk_card]:
            card.setFixedHeight(80)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setStyleSheet("""
                background: rgba(255,255,255,0.12);
                padding: 15px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            """)
            kpi_layout.addWidget(card)

        # MAIN
        main_layout = QHBoxLayout()

        self.sidebar = QListWidget()
        self.sidebar.addItems(["📊 Dashboard", "💾 Export CSV", "❌ Exit"])
        self.sidebar.clicked.connect(self.handle_menu)
        self.sidebar.setFixedWidth(140)

        main_layout.addWidget(self.sidebar)

        # LEFT
        left_panel = QVBoxLayout()

        self.table_card = GlassCard()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Amount","Hour","Location","Result"]
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                color: white;
                gridline-color: #2a2f45;
            }
            QTableWidget::item:hover {
                background-color: rgba(59,130,246,0.30);
            }
        """)

        self.table.verticalHeader().setVisible(False)

        table_layout.addWidget(QLabel("📋 Transactions"))
        table_layout.addWidget(self.table)

        self.table_card.setLayout(table_layout)
        left_panel.addWidget(self.table_card)

        # ALERT
        self.alert_card = GlassCard()
        alert_layout = QVBoxLayout()

        self.alert_label = QLabel("🚨 No Alerts")

        alert_layout.addWidget(QLabel("⚠️ Alerts"))
        alert_layout.addWidget(self.alert_label)

        self.alert_card.setLayout(alert_layout)
        left_panel.addWidget(self.alert_card)

        main_layout.addLayout(left_panel)

        # RIGHT GRAPH
        right_panel = QVBoxLayout()

        self.graph = pg.PlotWidget()
        self.graph.setBackground(None)
        self.graph.showGrid(x=True,y=True)

        right_panel.addWidget(QLabel("📊 Risk + Amount Trends"))
        right_panel.addWidget(self.graph)

        main_layout.addLayout(right_panel)

        # FINAL LAYOUT
        container = QVBoxLayout()
        container.addLayout(kpi_layout)
        container.addLayout(main_layout)

        self.setLayout(container)

        # MULTI GRAPH DATA
        self.x = []
        self.risk_data = []
        self.amount_data = []

        self.risk_curve = self.graph.plot(
            pen='r',
            name="Risk"
        )

        self.amount_curve = self.graph.plot(
            pen='b',
            name="Amount"
        )

        # SOUND
        self.alert_sound = QSoundEffect()
        sound_path = os.path.abspath("alert.wav")
        self.alert_sound.setSource(
            QUrl.fromLocalFile(sound_path)
        )
        self.alert_sound.setVolume(0.8)

        # TIMER
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

        # 🧠 anomaly detection
        is_anomaly = detect_anomaly(
            txn["amount"],
            txn["hour"],
            txn["location_change"]
        )

        result_str = str(result)

        row = self.table.rowCount()
        self.table.insertRow(row)

        amount_item = QTableWidgetItem(
            f"₹{txn['amount']}"
        )

        hour_item = QTableWidgetItem(
            str(txn["hour"])
        )

        loc_item = QTableWidgetItem(
            str(txn["location_change"])
        )

        result_item = QTableWidgetItem()

        # FRAUD / ANOMALY
        if is_anomaly or "Fraud" in result_str or result == 1:

            color = QColor(255,0,0,80)

            if is_anomaly:
                result_item.setText("⚠️ Anomaly")
                self.alert_label.setText(
                    "⚠️ Anomaly Detected!"
                )
            else:
                result_item.setText("🚨 Fraud")
                self.alert_label.setText(
                    f"🚨 Fraud: ₹{txn['amount']}"
                )

            self.fraud_total += 1

            if not self.alert_sound.isPlaying():
                self.alert_sound.play()

        else:

            color = QColor(0,255,0,60)

            result_item.setText("✅ Legit")

            self.legit_total += 1

            self.alert_label.setText(
                "✅ System Normal"
            )

        for item in [
            amount_item,
            hour_item,
            loc_item,
            result_item
        ]:
            item.setBackground(color)

        self.table.setItem(row,0,amount_item)
        self.table.setItem(row,1,hour_item)
        self.table.setItem(row,2,loc_item)
        self.table.setItem(row,3,result_item)

        self.table.scrollToBottom()

        # KPI
        total = self.fraud_total + self.legit_total

        risk = (
            self.fraud_total / total * 100
            if total else 0
        )

        self.fraud_card.setText(
            f"🚨 Fraud: {self.fraud_total}"
        )

        self.legit_card.setText(
            f"✅ Legit: {self.legit_total}"
        )

        self.risk_card.setText(
            f"⚠️ Risk: {risk:.1f}%"
        )

        # MULTI GRAPH UPDATE
        self.x.append(len(self.x))

        self.risk_data.append(risk)

        scaled_amount = txn["amount"]/1000
        self.amount_data.append(
            scaled_amount
        )

        self.risk_curve.setData(
            self.x,
            self.risk_data
        )

        self.amount_curve.setData(
            self.x,
            self.amount_data
        )


    def handle_menu(self,index):

        if "Export" in index.data():
            self.export_csv()

        elif "Exit" in index.data():
            self.close()


    def export_csv(self):

        with open(
            "transactions.csv",
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                ["Amount","Hour","Location","Result"]
            )

            for row in range(
                self.table.rowCount()
            ):
                writer.writerow([
                    self.table.item(row,col).text()
                    if self.table.item(row,col)
                    else ""
                    for col in range(4)
                ])

        self.alert_label.setText(
            "✅ Exported"
        )