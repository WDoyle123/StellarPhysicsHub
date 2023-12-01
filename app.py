from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import pandas as pd

try:
    with open('secretkey.txt', 'r') as file:
        secret_key = file.read()

except FileNotFoundError:
        secret_key = 'secret_key'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///objects.db'
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import Constellation, Star, User, LoginForm, RegisterForm

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def add_contribution_points(user_id, points=1):
    user = User.query.get(user_id)
    if user:
        user.points += points
        db.session.commit()

@app.route("/")
def index():
    layout = 'layout_logged_in.html' if current_user.is_authenticated else 'layout.html'
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    asterism_names = []#asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names

    return render_template('index.html', objects=objects, layout=layout)

@app.route('/login', methods=['GET', 'POST'])
def login():
    layout = 'layout_logged_in.html' if current_user.is_authenticated else 'layout.html'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
        else:
            # when login fails
            render_template('login.html',form=form, layout=layout)
    return render_template('login.html', form=form, layout=layout)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))
    

@app.route('/profile')
@login_required
def profile():
    layout = 'layout_logged_in.html' if current_user.is_authenticated else 'layout.html'
    return render_template('profile.html', user=current_user, layout=layout)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/contribute', methods=['GET', 'POST'])
@login_required
def contribute():
    layout = 'layout_logged_in.html' if current_user.is_authenticated else 'layout.html'
    if request.method == 'POST':
        # Extract data from the form
        name = request.form.get('name')
        body = request.form.get('body')
        description = request.form.get('description')
        stars_in_body = request.form.get('stars_in_body')

        if body == 'constellation':
            existing_constellation = Constellation.query.filter_by(name=name).first()
            if existing_constellation is None:
                new_constellation = Constellation(name=name, description=description, stars=stars_in_body)
                db.session.add(new_constellation)
                db.session.commit()
                add_contribution_points(current_user.id)  # Add points to the contributor
            else:
                return redirect(url_for('index'))

        elif body == 'asterism':
            existing_asterism = Asterism.query.filter_by(name=name).first()
            if existing_asterism is None:
                new_asterism = Asterism(name=name, description=description, stars=stars_in_body)
                db.session.add(new_asterism)
                db.session.commit()
                add_contribution_points(current_user.id)  # Add points to the contributor
            else:
                return redirect(url_for('index'))

        return redirect(url_for('index'))
    else:
        # GET request, just render the empty form
        return render_template('contribute.html', layout=layout)

@app.route('/constellation/<name>')
def constellation(name):
    layout = 'layout_logged_in.html' if current_user.is_authenticated else 'layout.html'
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    asterism_names = []#asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names

    constellation = Constellation.query.filter_by(name=name).first_or_404()
    stars = Star.query.filter_by(constellation_id=constellation.id)

    star_details = [
        {
            'name': star.common_name,
            'alt' : star.alt_name,
            'notes': star.note,
            'source': star.source,
            'distance': round(star.parsecs, 2),
            'right_ascension': round(star.right_acension, 2),
            'declination': round(star.declination, 2)
        }
        for star in stars
    ]

    star_names = [star.common_name for star in stars if star.common_name is not None and pd.notna(star.common_name)]
    star_names.sort()
    has_notes = any(star.get('notes') for star in star_details)
    return render_template('body.html', body=constellation, stars=star_details, star_names=star_names, has_notes=has_notes, of_type='Constellation', objects=objects, layout=layout)

@app.route('/asterism/<name>')
def asterism(name):
    layout = 'layout_logged_in.html' if current_user.is_authenticated else 'layout.html'
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    asterism_names = [asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names

    asterism = Asterism.query.filter_by(name=name).first_or_404()
    return render_template('body.html', body=asterism, of_type='Asterism', objects=objects, layout=layout)

@app.route("/search")
def search():
    query = request.args.get('query').strip()

    # Check if the query matches a constellation
    constellation = Constellation.query.filter_by(name=query).first()
    if constellation:
        return redirect(url_for('constellation', name=constellation.name))

    # Check if the query matches an asterism
    asterism = Asterism.query.filter_by(name=query).first()
    if asterism:
        return redirect(url_for('asterism', name=asterism.name))

    # If no matches, redirect to a default page or search results
    return redirect(url_for('index'))  # Or a different route for search results

@app.route('/wiki')
def wiki():
    layout = 'layout_logged_in.html' if current_user.is_authenticated else 'layout.html'
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    constellation_names.sort()
    asterism_names = []#asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names
    return render_template('wiki.html', constellation_names=constellation_names, asterism_names=asterism_names,objects=objects, layout=layout)

with app.app_context():
    db.create_all()

migrate = Migrate(app, db)
