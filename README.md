# timelogger
Provides the user with a GUI (wxpython) with a start and a stop button (and some extra stuff).
Start and stop times are saved in a csv file, and some work-related settings are displayed.

Run `pyinstaller.exe .\main.py --ico clock.ico` to get an executable
Join-Path -Path (Get-Item .).Fullname -ChildPath 'clock.ico'
cp .\clock.ico .\dist\main\
