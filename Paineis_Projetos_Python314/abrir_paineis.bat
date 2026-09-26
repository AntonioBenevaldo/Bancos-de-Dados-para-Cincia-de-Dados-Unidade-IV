@echo off
py -3.14 "%~dp0painel.py" %*
if errorlevel 1 pause
