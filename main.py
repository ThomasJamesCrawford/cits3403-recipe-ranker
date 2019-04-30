from app import app

# for flask shell pre import
from app import db
from app.models import User, Poll, Recipe, Vote


# for flask shell context processing
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Poll': Poll, 'Recipe': Recipe, 'Vote': Vote}
