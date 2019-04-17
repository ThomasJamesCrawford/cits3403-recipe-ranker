import os

class Config(object):
    # example secret key, for later use
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
