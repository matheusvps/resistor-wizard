@echo off
setlocal enabledelayedexpansion

:: Configuration
set "remoteUser=wizard"
set "remoteHost=resistorwizard.local"
set "remoteFilePath=~/ResistorWizard/main/photo.png"
set "localFolderPath=resistor-wizard\Backend\Fotos_Resistores"

:: Count existing files in the destination folder
set "fileCount=0"
for %%F in ("%localFolderPath%\*.png") do (
    set /a "fileCount+=1"
)

:: Increment the file count for the new file name
set /a "newFileCount=fileCount + 1"
set "newFileName=0000!newFileCount!.png"
set "localFilePath=%localFolderPath%\!newFileName!"

:: Download the file using scp
scp %remoteUser%@%remoteHost%:%remoteFilePath% "%localFilePath%"

echo File downloaded and saved as: %newFileName%
