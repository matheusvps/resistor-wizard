@ECHO OFF

ECHO --------------------------------------------------
ECHO Starting upload...

scp -r ./RPi wizard@resistorwizard.local:~/ResistorWizard

PAUSE
cls