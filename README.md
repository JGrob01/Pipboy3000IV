Windows Development:
cd F:\Pipboy3000IV
python -m venv .venv
.venv\Scripts\activate #venv/scripts/activate
$env:PIPBOY_DEV=1
python main.py

pyuic5 Pipboy3000IV.ui -o ui_test.py
pyuic5 boot.ui -o boot.py

-------------------------------------------------------------------------------------------------------------------------------------

Windows SSH:
ssh pipboy3000iv@pipboy3000iv.local
cd Pipboy3000IV
python3 -m venv .venv --system-site-packages
source .venv/bin/activate #source venv/bin/activate
git pull
QT_QPA_PLATFORM=eglfs python app.py

-------------------------------------------------------------------------------------------------------------------------------------

Pipboy Colors:
RGB:    26,255,9
        51,51,51