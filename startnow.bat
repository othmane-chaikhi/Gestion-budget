@echo off

REM Chemin vers votre environnement virtuel
SET VENV_PATH=.\

REM Chemin vers votre répertoire de projet Django
SET PROJECT_PATH=gestion_budget\

REM Activer l'environnement virtuel
CALL %VENV_PATH%\Scripts\activate.bat

REM Aller au répertoire du projet Django
cd %PROJECT_PATH%

REM Démarrer le serveur Django
start "" python manage.py runserver

REM Attendre un court instant pour que le serveur démarre
timeout /t 2 /nobreak >nul

REM Ouvrir Google Chrome avec l'URL du serveur Django
start chrome "http://127.0.0.1:8000/"

REM Attendre un court instant pour que le serveur démarre
timeout /t 5 /nobreak >nul

REM Ouvrir Visual Studio Code dans le répertoire du projet
start code .

REM
pause
