from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


# TODO allow login with either username or email
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# TODO
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={'type': 'email'})  # client side email validation
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Is an Admin')
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class RecipesSubForm(FlaskForm):
    class Meta:
        csrf = False  # subform doesnt need csrf token

    name = StringField(
        'Recipe Name', validators=[DataRequired()])
    description = StringField(
        'Recipe Description', validators=[DataRequired()])


class PollForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    recipes = FieldList(
        FormField(RecipesSubForm),
        validators=[])
    submit = SubmitField('Submit Poll')


class RecipeForm(FlaskForm):
    name = StringField('Recipe Name', validators=[DataRequired()])
    description = StringField(
        'Recipe Description', validators=[DataRequired()])
    poll = SelectField('Select Poll', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Submit Recipe')

