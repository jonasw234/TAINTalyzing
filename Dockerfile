FROM python:3.7-alpine
MAINTAINER Jonas A. Wendorf <jonas_wendorf@mail.de>
RUN apk add libmagic
COPY Projekt/ /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pipenv install --ignore-pipfile
ENTRYPOINT ["pipenv", "run", "python", "main.py"]
# Example run:
# docker build . -t taintalyzing
# docker run --rm -v "$(pwd)/appdata":/appdata taintalyzing /appdata/INPUT -o /appdata/REPORT.html
# Don't forget to also copy `customize.js`, `logo.png`, and `style.css` into the output directory if
# you use HTML report output.
# If you use Docker Toolbox on Windows, please see this link on how to use directories outside of
# C:\Users for your volumes: https://support.divio.com/local-development/docker/how-to-use-a-directory-outside-cusers-with-docker-toolboxdocker-for-windows
