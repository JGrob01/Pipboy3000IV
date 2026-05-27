ssh pipboy3000iv@pipboy3000iv.local

Install PyQt5
In PowerShell, navigate to where you want the project to live and set up a venv:
cd C:\Users\John
mkdir pipboy
cd pipboy
python -m venv .venv
.venv\Scripts\activate
Your prompt should now show (.venv) at the front. That means you're inside the virtual environment — packages you install here won't pollute your system Python.
pip install PyQt5
That gives you the library plus pyuic5 (the tool that converts Designer's .ui files into Python).
Verify it works
Make a file hello.py in the pipboy folder:
pythonfrom PyQt5.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel("PIP-BOY ONLINE")
label.setStyleSheet("background: #0a1a0a; color: #15ff60; "
                    "font-family: 'Courier New'; font-size: 32px; padding: 40px;")
label.show()
sys.exit(app.exec_())
Run it:
python hello.py
A small green-on-black window should appear. If it does, PyQt5 is working.
Understanding the Designer workflow
Here's how the pieces fit together — worth knowing before you build anything real:

You open Qt Designer, drag widgets around, save as mainwindow.ui (it's XML).
You convert that to Python with pyuic5:

   pyuic5 mainwindow.ui -o ui_mainwindow.py
This generates a Python class describing the layout. Don't edit this file — you'll regenerate it every time you change the design in Designer.
3. In your real code, you import that generated class and subclass it to add behavior (button clicks, data, etc.).
That separation is the key idea: Designer owns the layout, your hand-written code owns the behavior. When you tweak the UI in Designer, you re-run pyuic5 and your behavior code keeps working.
Try the full loop once
Open Qt Designer, choose "Main Window" as the template, drop a button and a label on it, save as test.ui in your pipboy folder. Then:
pyuic5 test.ui -o ui_test.py
Open ui_test.py and skim it — just so you can see what Designer is generating. Then make app.py:
pythonfrom PyQt5.QtWidgets import QApplication, QMainWindow
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
Run it — you should see exactly what you designed.
That's the full Designer → PyQt5 loop. Once you've done it once, the pattern is the same forever: design, convert, subclass, run.
A few things worth knowing now:

You don't have to use Designer. Some PyQt devs build everything in code because layouts get easier to diff in Git and reason about programmatically. For a Pip-Boy with lots of custom-painted widgets and animations, you'll likely end up doing more in code than in Designer anyway. Use Designer for static screens, hand-code the fancy stuff.
pyuic5 is just a script in your venv. If it says "not found," your venv isn't activated.
Designer can't preview your stylesheet very accurately — colors and fonts will look different at runtime. Don't worry about pixel-perfect previews in Designer; run the app to see the real thing.

Try the Designer round-trip and let me know when the window opens. Then we can talk about whether to lean on Designer or hand-code for the Pip-Boy.