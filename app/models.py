from app import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# query functions
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# users table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # not null and unique by default
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(128), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    date_registered = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    polls = db.relationship("Poll", backref='creator', lazy='dynamic')  # dynamic so we can filter the queries later
    recipes = db.relationship("Recipe", backref='contributor', lazy='dynamic')
    votes = db.relationship("Vote", backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# polls table
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipes = db.relationship("Recipe", backref='poll', lazy='dynamic')
    votes = db.relationship("Vote", backref='poll', lazy='dynamic')

    def __repr__(self):
        return '<Poll {}>'.format(self.name)


# recipes table
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    votes_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<Poll {}>'.format(self.name)


# votes table
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Vote {}>'.format(self.id)
