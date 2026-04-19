from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(300, 200, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Login")
        layout.addWidget(self.label)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        self.button = QPushButton("Login")
        self.button.clicked.connect(self.login)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.on_login_success = on_login_success

    def login(self):
        if self.username.text() == "admin" and self.password.text() == "1234":
            self.on_login_success()
            self.close()
        else:
            self.label.setText("Invalid credentials")