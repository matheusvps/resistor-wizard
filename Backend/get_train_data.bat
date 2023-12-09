@ECHO OFF

ECHO --------------------------------------------------
ECHO Starting upload...

scp -r wizard@resistorwizard.local:~/ResistorWizard/RPi/NOCROP ./

PAUSE
cls