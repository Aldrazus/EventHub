from flask import Flask, render_template, request, session, url_for, redirect, g
from blueprints.user_auth import user_auth



app = Flask(__name__)
app.register_blueprint(user_auth)

@app.before_request
def before_request():
    g.user = None
    if 'username' in session:
        g.user = session['username']

app.secret_key = 'not a good secret'

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)