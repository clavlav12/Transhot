@echo off
if not "%~1" =="" (goto exists)
set /p file=Enter File Path:
goto gotEverything

:exists
set file=%1%
goto gotEverything

:gotEverything
set
for %%f in ("%file%") do set filename=%%~nf
C:\Users\aviro\AppData\Local\Programs\Python\Python37\Scripts\pyuic5.exe -x %file% -o %filename%.py