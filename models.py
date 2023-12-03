from app import db
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class Constellation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    stars = db.relationship('Star', backref='constellation', lazy=True)
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contributor = db.relationship('User', backref='constellations', lazy=True)

class Star(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alt_name = db.Column(db.String(50), nullable=False)
    hr_name = db.Column(db.String(50), nullable=False)
    common_name = db.Column(db.String(50), nullable=True)
    right_acension = db.Column(db.Float(), nullable=False)
    declination = db.Column(db.Float(), nullable=False)
    bv_colour = db.Column(db.Float(), nullable=False)
    vmag = db.Column(db.Float(), nullable=True)
    parsecs = db.Column(db.Float(), nullable=False)
    note = db.Column(db.Text(), nullable=True)
    source = db.Column(db.Text(), nullable=True)
    constellation_id = db.Column(db.Integer, db.ForeignKey('constellation.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, default=0)

