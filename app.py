#!/usr/bin/python3
import json
import os
from schema import User
from schema import db
from schema import app
from flask import Flask, abort, render_template
from flask import request, session, send_from_directory
from tools import *

#app = Flask(__name__)

@app.route('/')
def landing():
	if not session.get('user'):
		name = ""
		logged_in = False;
	else:
		name = session.get('user')
		logged_in = True;
	return render_template("index.html",username=name,loggedIn=logged_in)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(name=username).first()
    if(user is None):
        return 'That user does not exist.'
    else:
        return 'Hello, %s.' % (username)

@app.route('/login',methods=['POST'])
def login():
    if not request.json:
        abort(400)
    data = request.get_json()
    if "username" not in data or "password" not in data:
        abort(400)
    result = User.query.filter_by(name=data["username"],password=hashText(data["password"])).first()
    if(result is None):
        return "Failed authentication"
    session['user'] = data['username']
    return "Authenticated"

@app.route('/logout')
def logout():
    if "user" in session:
        del session['user']
    return "Logged out."

@app.route('/signup',methods=['POST'])
def signup():
	if not request.json:
		abort(400)
	data = request.get_json()
	if "username" not in data or "password" not in data or "email" not in data:
		abort(400)
	try:
		data["username"] = str(data["username"])
		data["password"] = str(data["password"])

		if(len(data["username"])<4):
			return "-1: Username must be at least four characters"
		if(len(data["password"])<8):
			return "-2: Password must be at least eight characters"
		if(not matchExpression(data["email"],"[^@]+@[^@]+\.[^a]+")):
			return "-3: Invalid Email Address"
		if(not matchExpression(data["password"],"^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)")):
			return "-4: Passwords must have 1 lowercase letter, 1 uppercase letter and 1 number"
		if(User.query.filter_by(name=data["username"]).first() is not None):
			return "-5: That username is already taken!"
		if(User.query.filter_by(email=data["email"]).first() is not None):
			return "-6: That email is already taken!"
		newUser = User(name=data["username"],password=hashText(data["password"]),email=data["email"])
		db.session.add(newUser)
		db.session.commit()
	except Exception as e:
		return "-99: Unable to create new user"
	return "0: New user created."

@app.route("/redbridge/join",methods=['POST'])
def joinGame():
	if not request.json:
		abort(400)
	data = request.get_json()
	##Computing to check if game exists
	#return "-1: Invalid Game Code"
	return "0: OK"

@app.route('/js/<path:path>')
def retrieve_js(path):
    return send_from_directory('js',path)

@app.route('/css/<path:path>')
def retrieve_css(path):
    return send_from_directory('css',path)

@app.route('/client/<path:path>')
def retrieve_file(path):
	return send_from_directory('client',path)

#Generate session key
app.secret_key = os.urandom(12)

if __name__ == "__main__":
	app.run(host="0.0.0.0",port=80,debug=True)
