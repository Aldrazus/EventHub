from flask import Blueprint, render_template, request, session, url_for, redirect, g
from models.auth import hash_password, check_password
import pymysql.cursors

user_auth = Blueprint('user_auth', __name__,
                        template_folder='templates')

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='password',
                       db='event_hub',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@user_auth.route('/')
def login():
    return render_template("login.html")

@user_auth.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

@user_auth.route('/auth-student', methods=['POST'])
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

@user_auth.route('/auth-host', methods=['POST'])
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