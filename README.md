# COVID-19 Flask App

Flask App to visualize the spread of the COVID-19 pandemic.

# Setup Instructions

Install [pyenv](https://github.com/pyenv/pyenv) and set **python3.8.2** as the global interpreter version:
```
pyenv install 3.8.2
pyenv global 3.8.2
```
Make sure you have successfully installed pyenv:

`pyenv version`: 3.8.2 (set by $HOME/.pyenv/version)

Install [poetry](https://python-poetry.org/):
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
```
Install dependencies:
````
poetry install
```
# Start App
Run app:
```
flask run
```
Open in browser:
```
xdg-open http:127.0.0.1:5000/
```
