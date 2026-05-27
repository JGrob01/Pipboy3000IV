Windows Development:
cd F:\Pipboy3000IV
python -m venv .venv
.venv\Scripts\activate      -- activate virtual environment
python app.py               -- run application

pyuic5 Pipboy3000IV.ui -o ui_test.py    -- example QT Designer to Python Script

-------------------------------------------------------------------------------------------------------------------------------------

Windows SSH:
ssh pipboy3000iv@pipboy3000iv.local
cd Pipboy3000IV
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
T_QPA_PLATFORM=eglfs python hello.py

git pull