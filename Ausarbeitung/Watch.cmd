@echo off
set MAINFILE=Ausarbeitung
title Watching for changes in %MAINFILE% ...

:: Start additional programs if necessary
if exist %MAINFILE%.pdf start %MAINFILE%.pdf
if exist Literatur.bib start Literatur.bib

:: Watch for changes
watchexec -c -p -e bib,tex LaTeX-Watch-and-Build.cmd %MAINFILE%.tex
