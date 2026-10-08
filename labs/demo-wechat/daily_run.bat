@echo off
rem ============================================================
rem  Daily auto-run for demo-wechat (他律手记)
rem  Generates one draft per day (auto-approved), writes a log.
rem  Schedule with Task Scheduler, e.g.:
rem    schtasks /Create /TN "TaLvShouJi-Daily" /SC DAILY /ST 08:30 ^
rem      /TR "\"%~f0\""
rem  NOTE: keep this file ASCII-only + CRLF.
rem ============================================================
setlocal
set "ROOT=%~dp0"
set "PY=%ROOT%..\..\.venv\Scripts\python.exe"
set "LOG=%ROOT%workspace\logs"
if not exist "%LOG%" mkdir "%LOG%"
echo [%date% %time%] run start >> "%LOG%\daily.log"
if not exist "%PY%" (
  echo [%date% %time%] venv python not found: %PY% >> "%LOG%\daily.log"
  exit /b 1
)
"%PY%" "%ROOT%run_daily.py" --auto-approve >> "%LOG%\daily.log" 2>&1
echo [%date% %time%] run end (exit=%errorlevel%) >> "%LOG%\daily.log"
endlocal
