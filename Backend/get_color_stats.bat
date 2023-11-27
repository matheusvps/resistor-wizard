@ECHO OFF

ECHO --------------------------------------------------
ECHO Starting upload...

scp -r wizard@resistorwizard.local:~/ResistorWizard/RPi/COLOR_CLASSES ./RPi

PAUSE
cls