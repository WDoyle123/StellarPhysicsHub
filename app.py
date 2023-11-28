from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

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

from models import Constellation, Asterism, Star, User

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
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    asterism_names = [asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names

    return render_template('index.html', objects=objects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
        else:
            # when login fails
            render_template('login.html',form=form)
    return render_template('login.html', form=form)

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
    if request.method == 'POST':
        # Extract data from the form
        name = request.form.get('name')
        body = request.form.get('body')
        description = request.form.get('description')
        stars_in_body = request.form.get('stars_in_body')
        gif_url = request.form.get('gif_url')

        if body == 'constellation':
            existing_constellation = Constellation.query.filter_by(name=name).first()
            if existing_constellation is None:
                new_constellation = Constellation(name=name, description=description, gif_url=gif_url)
                # add_contribution_points(contributor_id)
                db.session.add(new_constellation)
            else:
                redirect(url_for('index'))

        elif body == 'asterism':
            existing_asterism = Asterism.query.filter_by(name=name).first()
            if existing_asterism is None:
                new_asterism = Asterism(name=name, description=description, gif_url=gif_url)
                # add_contribution_points(contributor_id)
                db.session.add(new_asterism)
            else:
                redirect(url_for('index'))

        db.session.commit()
        return redirect(url_for('index'))
    else:
        constellation_names = [constellation.name for constellation in Constellation.query.all()]
        asterism_names = [asterism.name for asterism in Asterism.query.all()]
        objects = asterism_names + constellation_names

        # GET request, just render the empty form
        return render_template('contribute.html', objects=objects)

@app.route('/constellation/<name>')
def constellation(name):
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    asterism_names = [asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names

    constellation = Constellation.query.filter_by(name=name).first_or_404()
    return render_template('body.html', body=constellation, of_type='Constellation', objects=objects)

@app.route('/asterism/<name>')
def asterism(name):
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    asterism_names = [asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names

    asterism = Asterism.query.filter_by(name=name).first_or_404()
    return render_template('body.html', body=asterism, of_type='Asterism', objects=objects)

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
    constellation_names = [constellation.name for constellation in Constellation.query.all()]
    asterism_names = [asterism.name for asterism in Asterism.query.all()]
    objects = asterism_names + constellation_names
    return render_template('wiki.html', constellation_names=constellation_names, asterism_names=asterism_names,objects=objects)

with app.app_context():
    db.create_all()

migrate = Migrate(app, db)
