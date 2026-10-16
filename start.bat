@echo off
title Telegram Chat Summarizer
echo.
echo  Starting Telegram Chat Summarizer...
echo  =====================================
echo.

cd /d D:\Projects\telegram-summarizer
call venv\Scripts\activate
python main.py

pause
