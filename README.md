**ATTENTION**: I haven’t updated this repository for quite a while and I’m not sure when I’ll get the time to again.  Work is keeping me pretty busy and there is a new kid on the block with [CodeQL](https://securitylab.github.com/tools/codeql), which pretty much makes this project obsolete because it does pretty much what TAINTalyzing set out to do but has more active support and development behind it (whereas TAINTalyzing was a one-man-job for a few months).  I recommend you give [CodeQL](https://securitylab.github.com/tools/codeql) a try and see if you like it :)!

# TAINTalyzing

An easy to extend static code analysis framework.

[![snapshot](/Präsentation/video/snapshot.png)](/Präsentation/video/cfiles.mkv)

Please see either the `Dockerfile`, or `Projekt/INSTALL.md` for instructions on how to install and
use the framework.

The framework uses static code analysis to try to find potentially user controlled inputs and
potentially security critical functions and whether there is a connection between the two.  It will
then output its findings to make searching for vulnerabilities in your source codes easier.

One of the main intents of the framework is to be easily extensible, such that users can easily
create new modules to allow additional programming languages to be supported as well as new rulesets
to use with these modules.

## Folder “Ausarbeitung”

Contains my master thesis and all the theoretical background for the framework (German only, sorry).

Important files:
- `.latexmkrc`: Used for `latexmk` to compile the source files
- `Generate Print Versions.cmd`: Converts color images from `img/Digital` to black and white images
  under `img/Druck`
- `LaTeX-Watch-and-Build.cmd`: Generates tags file for Vim, `latexmk` to compile source files,
  `TeXLogAnalyser` to pretty print errors and warnings during the compilation, `chktex` to check for
  common errors in LaTeX sources and LanguageTool to find grammatical mistakes.  Results are also
  stored in subdirectory `logs`.
- `Literatur.bib`: BibLaTeX file with sources
- `Watch.cmd`: Uses `watchexec` to watch for changes in the LaTeX sources, calls
  `LaTeX-Watch-and-Build.cmd` with the changed files

## Folder “Präsentation”

Contains the presentation I gave to demonstrate the framework.

Important files:
- `.latexmkrc`: See above
- `example/*`: Example HTML report that I showcase in the presentation
- `LaTeX-Watch-and-Build.cmd`: See above
- `video/cfiles.mkv`: Video demonstration of the framework in action
- `video/layout.txt`: Layout configuration for Windows command shell window (prompt was set with
  `prompt $G `)
- `Watch.cmd`: See above

## Folder “Projekt”

The project files needed to run the framework.

Important files:
- `.flake8`: Configuration for Python code style checker `flake8`
- `.pylintrc`: Configuration for Python code style checker `Pylint`
- `checkstyle.{cmd,sh}`: Check for Python style violations
- `INSTALL.md`: Installation and usage instructions
- `install.{cmd,sh}`: Automatic install scripts.  If using 32 bit versions of Windows, you need to
  manually download GNU `file`
- `Makefile`: Used to generate documentation with `make html`
- `requirements.txt`: Prerequisites for the installation with `Pipenv`
- `Pipfile.lock`: Used for installation with `Pipenv`
- `Pipfile`: Used for installation with `Pipenv`
- `conf.py`: Configuration file for the documentation
- `custom.js`, `logo.png`, and `style.css`: Keep those in the same directory as the HTML report,
  customize if you want to
- `modules/*/grammar.py`: Grammar used to parse a programming language
- `modules/*/sinks/*.y{a,}ml`: Create rules for sinks and sanitizers here
- `modules/*/sources/*.y{a,}ml`: Create rules for sources here
- `modules/abstract_grammar.py`: When creating new grammars, use this as base class
- `modules/detection.txt`: Detection parameters for modules
- `run.{cmd,sh}`: Run the framework
- `testfiles/*`: Test files for unittests
- `unittest.{cmd,sh}`: Automatic unittests

## Where to find sink rules

To find rules for your vulnerability detection, you should search for the Security Development
Lifecycle.  For example [see this
article](https://docs.microsoft.com/en-us/previous-versions/bb288454(v=msdn.10)) from Microsoft for
examples of vulnerable functions in C and which alternatives to use.

Please note, that not all rules from these sites are incorporated and recommendations might differ.
Please think for yourself, which recommendation you can and want to follow.
