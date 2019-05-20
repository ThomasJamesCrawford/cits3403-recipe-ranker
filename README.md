# cits3403-recipe-ranker
CITS3403 Project: Social Choice

### The purpose of the web application
The purpose of the application is to find the best recipe from a selection curated by administrators.
The social choice mechanism to identify the best recipe is a first past the post polling system.
Each unique user gets one unique vote per poll for their first preference and the winning recipe is the one with the highest votes.

### The architecture of the web application
#### client side 
HTML5, CSS, Javascript/JQuery, Bootstrap 4

#### server side
Flask -  micro web framework for routing
    WTForms - form input handling and validation
    Flask-Login - user session management

SQLAlchemy - database engine

## running the flask app

### prerequisites
1. install python version 3
2. install pip for python
3. `pip install virtualenv` to install virtualenv

### python environment setup
1. `virtualenv --python=/usr/bin/python3.7 venv` or `virtualenv venv` to create virtual environment (we are using version 3.7)
2. `source venv/bin/activate` to activate, `venv\Scripts\activate` to activate in MS Windows
3. `deactivate` to deactivate or go back to main python environment

### python pip setup
- `pip install -r requirements.txt` to install flask, jinja2, etc

### run the app
1. make sure working directory is at the root of the project folder
2. `export FLASK_APP=main.py` assigns the system environment variables (not necessary if python-dotenv is in requirements.txt)
3. `flask run` starts the server for the app
4. [http://127.0.0.1:5000/](http://127.0.0.1:5000/) is the output page

### python-dotenv (optional)
makes system environment variables automatically loaded from a file
- flask uses the file .flaskenv
- no need to `export FLASK_APP=main.py` manually, but it is in the file .flaskenv

### the database - ?not in final readme?
`flask db upgrade` - uses newest migration script, do this when source control has a new app.db
`flask db downgrade` - removes migration script
`flask db migrate` - generates migration script, do this when the models are changed

the db.Column etc in models.py will show errors from default linter swapping to flake8 seems to get rid of them
- ctrl+shift+p -> select linter -> flake8 

### unit tests
`python unittest test_unittests.py` - Runs all the unit tests and outputs results

### commit log

