@echo off
setlocal EnableExtensions
rem uv / other user-local tools (Git Bash often misses these vs PowerShell)
if exist "%USERPROFILE%\.local\bin" set "PATH=%USERPROFILE%\.local\bin;%PATH%"
set "BASH_EXE="
if defined GIT_BASH if exist "%GIT_BASH%" set "BASH_EXE=%GIT_BASH%"
if not defined BASH_EXE if exist "C:\Program Files\Git\bin\bash.exe" set "BASH_EXE=C:\Program Files\Git\bin\bash.exe"
if not defined BASH_EXE if exist "D:\git\Git\bin\bash.exe" set "BASH_EXE=D:\git\Git\bin\bash.exe"
if not defined BASH_EXE (
  echo Git Bash not found. Install Git for Windows or set GIT_BASH to bash.exe 1>&2
  exit /b 1
)
"%BASH_EXE%" %*
exit /b %ERRORLEVEL%
