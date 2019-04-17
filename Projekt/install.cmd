@echo off
pip install -r requirements.txt
pipenv install --ignore-pipfile

reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=32BIT || set OS=64BIT

if %OS%==64BIT goto 64BIT
copy file-windows-32\magic.mgc .
copy file-windows-32\magic1.dll .
goto :EOF

:64BIT
copy file-windows-64\magic.mgc .
copy file-windows-64\libmagic-1.dll magic1.dll
goto :EOF
