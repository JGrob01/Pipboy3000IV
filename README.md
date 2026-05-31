Windows Development:
cd F:\Pipboy3000IV
python -m venv .venv
venv/scripts/activate
$env:PIPBOY_DEV=1
python main.py

-------------------------------------------------------------------------------------------------------------------------------------

Windows SSH:
ssh pipboy3000iv@pipboy3000iv.local
cd Pipboy3000IV
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
git pull
QT_QPA_PLATFORM=eglfs python main.py

-------------------------------------------------------------------------------------------------------------------------------------