$ErrorActionPreference = 'Stop'
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py makemigrations
py manage.py migrate
py manage.py seed_demo
Write-Host "Setup complete. Run: py manage.py runserver"
