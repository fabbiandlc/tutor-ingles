@echo off
title English Tutor

echo.
echo  Iniciando English Tutor...
echo.

:: Arrancar backend (uvicorn)
start "Backend - English Tutor" cmd /k "cd /d C:\Users\FABIAN\Desktop\tutor-ingles\backend && venv\Scripts\activate && uvicorn app.main:app --port 8000"

:: Esperar a que el backend esté listo
timeout /t 4 /nobreak >nul

:: Arrancar servidor frontend
start "Frontend - English Tutor" cmd /k "cd /d C:\Users\FABIAN\Desktop\tutor-ingles\frontend && python -m http.server 3000"

:: Esperar un momento y abrir el navegador
timeout /t 2 /nobreak >nul
start "" "http://localhost:3000"

exit
