@echo off
set /p file=Enter File Path: 
set 
for %%f in ("%file%") do set filename=%%~nf
C:\Users\aviro\AppData\Local\Programs\Python\Python37\Scripts\pyrcc5.exe %file% -o %filename%_rc.py
pause