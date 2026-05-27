from PyQt5.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel("PIP-BOY ONLINE")
label.setStyleSheet("background: #0a1a0a; color: #15ff60; "
                    "font-family: 'Courier New'; font-size: 32px; padding: 40px;")
label.show()
sys.exit(app.exec_())