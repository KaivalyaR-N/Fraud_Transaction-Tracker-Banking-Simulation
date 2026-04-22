from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QFrame, QListWidget, QHeaderView
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
        QFrame{
            background: rgba(255,255,255,0.06);
            border:1px solid rgba(255,255,255,0.10);
            border-radius:22px;
        }
        """)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fraud Analytics Pro")
        self.showMaximized()

        self.setStyleSheet("""
        QWidget{
            background:qlineargradient(
                x1:0,y1:0,x2:1,y2:1,
                stop:0 #0F172A,
                stop:1 #111827
            );
            color:#E5E7EB;
            font-family:Segoe UI;
        }

        QLabel{
            background:transparent;
        }
        """)

        self.fraud_total = 0
        self.legit_total = 0
        self.anomaly_total = 0

        root = QHBoxLayout(self)
        root.setContentsMargins(28,28,28,28)
        root.setSpacing(24)

        # -------- SIDEBAR --------
        self.sidebar = QListWidget()
        self.sidebar.addItems([
            "Dashboard",
            "Export",
            "Exit"
        ])

        self.sidebar.clicked.connect(
            self.handle_menu
        )

        self.sidebar.setFixedWidth(180)

        self.sidebar.setStyleSheet("""
        QListWidget{
            background:rgba(255,255,255,0.05);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:22px;
            padding:14px;
        }

        QListWidget::item{
            padding:14px;
            margin:6px;
            border-radius:12px;
        }

        QListWidget::item:selected{
            background:rgba(255,255,255,0.08);
        }
        """)

        root.addWidget(self.sidebar)

        # -------- MAIN --------
        main = QVBoxLayout()
        main.setSpacing(22)

        # KPI
        kpi = QHBoxLayout()

        self.kpi1 = GlassCard()
        a = QVBoxLayout(self.kpi1)
        a.addWidget(QLabel("Fraud Signals"))
        self.fraud_label = QLabel("0")
        self.fraud_label.setStyleSheet(
            "font-size:30px;font-weight:700;"
        )
        a.addWidget(self.fraud_label)

        self.kpi2 = GlassCard()
        b = QVBoxLayout(self.kpi2)
        b.addWidget(QLabel("Legitimate Flow"))
        self.legit_label = QLabel("0")
        self.legit_label.setStyleSheet(
            "font-size:30px;font-weight:700;"
        )
        b.addWidget(self.legit_label)

        self.kpi3 = GlassCard()
        c = QVBoxLayout(self.kpi3)
        c.addWidget(QLabel("Risk Index"))
        self.risk_label = QLabel("0.0%")
        self.risk_label.setStyleSheet(
            "font-size:30px;font-weight:700;"
        )
        c.addWidget(self.risk_label)

        kpi.addWidget(self.kpi1)
        kpi.addWidget(self.kpi2)
        kpi.addWidget(self.kpi3)

        main.addLayout(kpi)

        # -------- CONTENT --------
        content = QHBoxLayout()

        # TABLE
        table_card = GlassCard()
        twrap = QVBoxLayout(table_card)

        twrap.addWidget(
            QLabel("Live Transactions")
        )

        self.table = QTableWidget()
        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(
            ["Amount","Hour","Location","Result"]
        )

        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            1,QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            3,QHeaderView.Stretch
        )

        self.table.setStyleSheet("""
        QTableWidget{
            background:transparent;
            border:none;
            gridline-color:rgba(255,255,255,0.05);
        }

        QHeaderView::section{
            background:rgba(255,255,255,0.08);
            border:none;
            padding:8px;
        }
        """)

        twrap.addWidget(self.table)

        content.addWidget(
            table_card,3
        )

        # GRAPH
        graph_card = GlassCard()
        gwrap = QVBoxLayout(graph_card)

        gwrap.addWidget(
            QLabel("Risk Trend")
        )

        self.graph = pg.PlotWidget()

        self.graph.setBackground(None)

        self.graph.showGrid(
            x=True,
            y=True,
            alpha=0.15
        )

        self.graph.getPlotItem().hideAxis("top")
        self.graph.getPlotItem().hideAxis("right")

        self.curve = self.graph.plot(
            pen=pg.mkPen(width=3)
        )

        gwrap.addWidget(self.graph)

        content.addWidget(
            graph_card,2
        )

        main.addLayout(content)

        root.addLayout(main,1)

        self.x=[]
        self.risk_series=[]

        # -------- ALERT SOUND --------
        self.alert_sound = QSoundEffect()

        sound_path = os.path.abspath(
            "alert.wav"
        )

        self.alert_sound.setSource(
            QUrl.fromLocalFile(
                sound_path
            )
        )

        self.alert_sound.setVolume(0.8)

        # TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(
            self.run_transaction
        )
        self.timer.start(1200)


    # -------- LIVE LOOP --------
    def run_transaction(self):

        txn = generate_transaction()

        result = str(
            predict_transaction(
                txn["amount"],
                txn["hour"],
                txn["location_change"]
            )
        )

        is_anomaly = detect_anomaly(
            txn["amount"],
            txn["hour"],
            txn["location_change"]
        )

        row = self.table.rowCount()

        self.table.insertRow(row)

        status="Legit"
        tint=QColor(0,255,0,30)

        if is_anomaly:

            status="Anomaly"

            tint=QColor(
                255,180,0,45
            )

            self.anomaly_total += 1

            if not self.alert_sound.isPlaying():
                self.alert_sound.play()


        elif "Fraud" in result:

            status="Fraud"

            tint=QColor(
                255,0,0,40
            )

            self.fraud_total += 1

            if not self.alert_sound.isPlaying():
                self.alert_sound.play()


        else:

            self.legit_total += 1


        vals = [
            f"₹{txn['amount']}",
            str(txn["hour"]),
            str(txn["location_change"]),
            status
        ]

        for c,v in enumerate(vals):

            item = QTableWidgetItem(v)

            item.setBackground(tint)

            self.table.setItem(
                row,c,item
            )

        self.table.scrollToBottom()

        total = (
            self.fraud_total +
            self.legit_total +
            self.anomaly_total
        )

        risk = (
            self.fraud_total/total*100
            if total else 0
        )

        self.fraud_label.setText(
            str(self.fraud_total)
        )

        self.legit_label.setText(
            str(self.legit_total)
        )

        self.risk_label.setText(
            f"{risk:.1f}%"
        )

        self.x.append(
            len(self.x)
        )

        self.risk_series.append(
            risk
        )

        self.curve.setData(
            self.x,
            self.risk_series
        )


    # -------- MENU --------
    def handle_menu(self,index):

        txt = index.data()

        if "Exit" in txt:
            self.close()

        elif "Export" in txt:
            self.export_csv()


    # -------- EXPORT --------
    def export_csv(self):

        with open(
            "transactions.csv",
            "w",
            newline=""
        ) as f:

            w = csv.writer(f)

            w.writerow([
                "Amount",
                "Hour",
                "Location",
                "Result"
            ])

            for r in range(
                self.table.rowCount()
            ):

                w.writerow([
                    self.table.item(r,c).text()
                    if self.table.item(r,c)
                    else ""
                    for c in range(4)
                ])

        print("Exported.")