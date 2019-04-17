$pdflatex = 'lualatex -synctex=1 %O %S';
$pdf_mode = 1;
$postscript_mode = $dvi_mode = 0;

add_cus_dep('glo', 'gls', 0, 'run_makeglossaries');
add_cus_dep('acn', 'acr', 0, 'run_makeglossaries');

push @generated_exts, 'glo', 'gls', 'glg', 'acn', 'acr', 'alg', 'synctex', 'synctex.gz';
$clean_ext .= '%R.bbl %R.lol %R.xdy %R.run.xml';

sub run_makeglossaries {
    if ( $silent ) {
        system("makeglossaries -q $_[0]");
    }
    else {
        system("makeglossaries $_[0]");
    };
}

