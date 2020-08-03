@echo off

mkdir build
cd build
pyinstaller --onefile ../__main__.py -i ../quicksendfiles.ico -n quicksendfiles.exe
move dist\quicksendfiles.exe ..
pause

