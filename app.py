from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_test import Ui_MainWindow
import sys

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())