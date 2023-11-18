@ECHO OFF

ECHO --------------------------------------------------
ECHO Starting upload...

scp globals.py wizard@resistorwizard.local:~/ResistorWizard/main/globals.py
scp utils.py wizard@resistorwizard.local:~/ResistorWizard/main/utils.py
scp rpi_main.py wizard@resistorwizard.local:~/ResistorWizard/main/main.py

PAUSE
cls