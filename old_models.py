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

constellation_asterism = db.Table('constellation_asterism',
    db.Column('constellation_id', db.Integer, db.ForeignKey('constellation.id'), primary_key=True),
    db.Column('asterism_id', db.Integer, db.ForeignKey('asterism.id'), primary_key=True)
)

star_constellation = db.Table('star_constellation',
    db.Column('star_id', db.Integer, db.ForeignKey('star.id'), primary_key=True),
    db.Column('constellation_id', db.Integer, db.ForeignKey('constellation.id'), primary_key=True)
)

star_asterism = db.Table('star_asterism',
    db.Column('star_id', db.Integer, db.ForeignKey('star.id'), primary_key=True),
    db.Column('asterism_id', db.Integer, db.ForeignKey('asterism.id'), primary_key=True)
)

class Constellation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    asterisms = db.relationship('Asterism', secondary=constellation_asterism, backref=db.backref('constellations', lazy='dynamic'))
    stars = db.relationship('Star', secondary=star_constellation, backref=db.backref('constellations', lazy='dynamic'))
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contributor = db.relationship('User')

class Asterism(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    stars = db.relationship('Star', secondary=star_asterism, backref=db.backref('asterisms', lazy='dynamic'))
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contributor = db.relationship('User')

class Star(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, default=0)

