@echo off
@title installer Chess.Com Stat Tracker & Auto q
pip install -r requirements.txt
cls
echo Starting Stat Tracker if it opens a vsc window or anything just close it and open the STATS-TRACKER.py file normally
START STATS-TRACK.PY
echo installed click enter to exit!
pause -nul