from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///objects.db'
db = SQLAlchemy(app)

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
    description = db.Column(db.Text, nullable=False)
    gif_url = db.Column(db.String(255))
    asterisms = db.relationship('Asterism', secondary=constellation_asterism, backref=db.backref('constellations', lazy='dynamic'))
    stars = db.relationship('Star', secondary=star_constellation, backref=db.backref('constellations', lazy='dynamic'))

class Asterism(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    gif_url = db.Column(db.String(255))
    stars = db.relationship('Star', secondary=star_asterism, backref=db.backref('asterisms', lazy='dynamic'))

class Star(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/contribute', methods=['GET', 'POST'])
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
                db.session.add(new_constellation)
            else:
                redirect(url_for('index'))

        elif body == 'asterism':
            existing_asterism = Asterism.query.filter_by(name=name).first()
            if existing_asterism is None:
                new_asterism = Asterism(name=name, description=description, gif_url=gif_url)
                db.session.add(new_asterism)
            else:
                redirect(url_for('index'))

        db.session.commit()
        return redirect(url_for('index'))
    else:
        # GET request, just render the empty form
        return render_template('contribute.html')

@app.route('/big_dipper')
def big_dipper():
    return render_template('big_dipper.html')

@app.route("/search")
def search():
    query = request.args.get('query')
    # Logic to decide where to redirect based on the query
    if query.lower() == 'big dipper':
        return redirect(url_for('big_dipper'))
    # Add more conditions for other searches or a default search result
    else:
        # Redirect to a default page or show search results
        return redirect(url_for('index'))

with app.app_context():
    db.create_all()

