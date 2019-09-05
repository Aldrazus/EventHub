from flask import Flask, render_template, request, session, url_for, redirect, g
import pymysql.cursors


app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='password',
                       db='event_hub',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def test():
    name = 'Alberto'
    data = None
    with conn.cursor() as cursor:
        query = 'SELECT * FROM person WHERE name = %s'
        cursor.execute(query, (name))
        data = cursor.fetchone()

    return (f'Hello World! {data["name"]} is {data["age"]} years old')

app.secret_key = 'not a good secret'

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)