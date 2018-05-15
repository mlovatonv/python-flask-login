import sys
import os
import MySQLdb
import json
from flask import Flask, render_template, session, request, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = '?'

cache = {}

connection = MySQLdb.connect (user = "mlovaton", db = "c9")
cursor = connection.cursor()
"""cursor.execute("CREATE TABLE Users (ID int UNIQUE, username varchar(255) NOT NULL, password varchar(255))")"""
"""cursor.execute("CREATE TABLE Messages (TIME int NOT NULL AUTO_INCREMENT, ID int, message varchar(255), PRIMARY KEY (TIME))")"""

cursor.execute("TRUNCATE TABLE Users")
cursor.execute("TRUNCATE TABLE Messages")

@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('chat'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    cursor.execute("select * from Users")
    data = cursor.fetchall()
    
    if request.method == 'POST':
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])
        for row in data:
            if POST_USERNAME == row[1] and POST_PASSWORD == row[2]:
                session['logged_in'] = True
                return redirect(url_for('chat'))
        return render_template('Error.html')
    return render_template('Login.html')   

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route('/chat', methods = ['GET', 'POST'])
def chat():
    if request.method == 'POST':
        key = 'getMessages'
        if key in cache.keys():
            del cache[key]
        
        POST_MESSAGE = str(request.form['message'])
        cursor.execute("INSERT INTO Messages (ID,message) VALUES (100,%s)", (POST_MESSAGE))
    return render_template('Chat.html')

@app.route('/messages')
def get_messages():
    cursor.execute("SELECT * FROM Messages")
    data = cursor.fetchall()
    
    key = 'getMessages'
    if key not in cache.keys():
        cache[key] = data;
        print("From DB")
    else:
        print("From Cache")
    
    messages = cache[key];
    response = []
    for message in messages:
        response.append(message)
    return json.dumps(response, cls=None)

@app.route('/get-message/<id>', methods = ['GET'])
def get_message(id):
    try:
        cursor.execute("SELECT * FROM Messages WHERE ID = %s", (id))
        data = cursor.fetchall()
        response = []
        for message in data:
            response.append(message[2])
        return json.dumps(response, cls=None)
    except:
        return "ERROR 404"
    
@app.route('/delete-message/<id>', methods = ['GET', 'DELETE'])
def delete_message(id):
    try:
        cursor.execute("DELETE FROM Messages WHERE ID = %s", (id))
    
        key = 'getMessages'
        if key in cache.keys():
            del cache[key]
    
        return "DELETED"
    except:
        return "ERROR 404"

@app.route('/setUsers')
def set_user():
    key = 'getUsers'
    if key in cache.keys():
        del cache[key]
    
    cursor.execute("INSERT INTO Users (ID, username,password) VALUES (100,'admin','123')")
    cursor.execute("INSERT INTO Users (ID, username,password) VALUES (101,'python','hola')")
    return 'Created users'

@app.route("/users")
def get_users():
    cursor.execute("select * from Users")
    data = cursor.fetchall()
    
    key = 'getUsers'
    if key not in cache.keys():
        cache[key] = data;
        print("From DB")
    else:
        print("From Cache")
    
    users = cache[key];
    
    return render_template('List_users.html', users=users)

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
    """app.run(debug = True)"""

