@echo off
rem ============================================================
rem  Daily auto-run for demo-wechat (????)  --  one log per day
rem  Generates one draft (auto-approved) + cover, writes a daily log.
rem  Schedule with Task Scheduler, e.g.:
rem    schtasks /Create /TN "TaLvShouJi-Daily" /SC DAILY /ST 08:30 /TR "\"%~f0\""
rem  NOTE: keep this file ASCII-only + CRLF.
rem ============================================================
setlocal
set "ROOT=%~dp0"
set "PY=%ROOT%..\..\.venv\Scripts\python.exe"
set "LOGDIR=%ROOT%workspace\logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

rem --- daily log file name: yyyy-MM-dd.log ---
set "DS="
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "DS=%%i"
if "%DS%"=="" set "DS=undated"
set "LOGFILE=%LOGDIR%\%DS%.log"

echo [%date% %time%] run start >> "%LOGFILE%"
if not exist "%PY%" (
  echo [%date% %time%] venv python not found: %PY% >> "%LOGFILE%"
  exit /b 1
)
"%PY%" "%ROOT%run_daily.py" --auto-approve >> "%LOGFILE%" 2>&1
echo [%date% %time%] run end (exit=%errorlevel%) >> "%LOGFILE%"
endlocal
