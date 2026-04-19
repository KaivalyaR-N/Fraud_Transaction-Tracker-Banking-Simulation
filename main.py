import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

# Start application
app = QApplication(sys.argv)

# Open main dashboard
window = MainWindow()
window.show()

# Run event loop
sys.exit(app.exec_())