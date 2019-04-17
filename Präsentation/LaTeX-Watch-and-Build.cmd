:: LaTeX-Watch-and-Build
:: Watch LaTeX files with watchexec, build with LatexMk, check the log file with pplatex, check the
:: sources with chktex and use LanguageTool as grammar checker for source file.
@echo off

if "%WATCHEXEC_CREATED_PATH%" == "" (
    echo This script must be called from watchexec only!
    exit /b
)
if "%1" == "" (
    echo Usage: %~nx0 MAIN.tex
    exit /b
)
cls

:: Remove leading \\?\
set WATCHEXEC_CREATED_PATH="%WATCHEXEC_CREATED_PATH:~4%"

:: Create output directory
if not exist logs\nul mkdir logs

:: Start message
echo Changes detected in file %WATCHEXEC_CREATED_PATH%
echo ===================
echo.

:: Regenerate tags file
echo Regenerating tags file
echo ===================
ctags -f tags --quiet --recurse=yes %1 tex
echo.

:: Build
echo Running LatexMk
echo ===================
latexmk %1 -interaction=nonstopmode > nul
echo.

:: Check LaTeX log file
echo Running TeXLogAnalyser
echo ===================
texloganalyser -aw %~n1.log
echo.

:: Check LaTeX source file
echo Running chktex
echo ===================
chktex -n 2 -n 8 -n 9 -n 11 -n 12 -n 13 -n 15 -n 17 -n 18 -n 26 -n 36 -n 37 %WATCHEXEC_CREATED_PATH% > logs\chktex.log 2>nul
type logs\chktex.log
echo.

:: Grammar check source file
echo Running LanguageTool
echo ===================
java -jar "C:\Program Files\LanguageTool\languagetool-commandline.jar" -c utf8 -d ABKUERZUNG_LEERZEICHEN,COMMA_PARENTHESIS_WHITESPACE,DE_CASE,GERMAN_SPELLER_RULE,TYPOGRAFISCHE_ANFUEHRUNGSZEICHEN,UNPAIRED_BRACKETS,UPPERCASE_SENTENCE_START,WHITESPACE_RULE,AUSLASSUNGSPUNKTE,DE_SENTENCE_WHITESPACE,DE_DOUBLE_PUNCTUATION,LEERZEICHEN_HINTER_DOPPELPUNKT,MALZEICHEN,LEERZEICHEN_NACH_VOR_ANFUEHRUNGSZEICHEN,LEERZEICHEN_RECHENZEICHEN,EINHEIT_LEERZEICHEN,GROESSERALS,FALSCHE_VERWENDUNG_DES_BINDESTRICHS -l de-DE --languagemodel "C:\Program Files\LanguageTool\ngrams" %WATCHEXEC_CREATED_PATH% > logs\languagetool.log 2>nul
type logs\languagetool.log
echo.
