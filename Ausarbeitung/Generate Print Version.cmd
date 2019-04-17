@ECHO OFF
FOR /R img\Digital\ %%A IN (*.png) DO (
    magick.exe "%%A" -trim "%%A"
    magick.exe "%%A" +gamma 0.6 -grayscale Average "%CD%\img\Druck\%%~nxA"
)
FOR /R img\Digital\ %%A IN (*.pdf) DO (
    gswin64c.exe -sDEVICE=pdfwrite -sProcessColorModel=DeviceGray -sColorConversionStrategy=Gray -dOverrideICC -o  "%CD%\img\Druck\%%~nxA" -f "%%A"
)
