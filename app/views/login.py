from flask import Blueprint, render_template, request, session, url_for, redirect, g
from app.models.auth import hash_password, check_password
import pymysql.cursors

mod = Blueprint('login', __name__,
                        template_folder='templates')

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='password',
                       db='event_hub',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@mod.route('/')
def login():
    return render_template("login.html")

@mod.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

@mod.route('/auth-student', methods=['POST'])
def auth_student():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()

    query = 'SELECT username, password FROM Student WHERE username = %s'
    cursor.execute(query, username)

    data = cursor.fetchone()
    cursor.close()
    if data and check_password(password, data['password']):
        session['username'] = username
        return redirect('/logged-in')
    else:
        return redirect('/')

@mod.route('/auth-host', methods=['POST'])
def auth_org():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()

    query = 'SELECT username, password FROM Host WHERE username = %s'
    cursor.execute(query, username)

    data = cursor.fetchone()
    cursor.close()
    if data and check_password(password, data['password']):
        session['username'] = username
        return redirect('/logged-in')
    else:
        return redirect('/')