$pdflatex = 'lualatex -synctex=1 %O %S';
$pdf_mode = 1;
$postscript_mode = $dvi_mode = 0;

push @generated_exts, 'run.xml', 'synctex', 'synctex.gz', 'vrb';
$clean_ext .= '%R.bbl';
