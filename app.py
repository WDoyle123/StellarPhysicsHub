from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

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
