import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests as rq
from datetime import datetime as dt
import json
#from flask_cors import CORS # for cross-origin resource sharing


HFurl = "https://hf-api.herokuapp.com/api/"
app_name = "Flask App Basic"


app = Flask(__name__)
#CORS(app) # for enabling cross-origin resource sharing

app.secret_key = secrets.token_hex(32)

@app.before_request
def before_request():
    path = request.path
    method = request.method
    if 'hfid' in session and int(session['verified']) - dt.timestamp(dt.now()) > 3600:
        url = HFurl + "hfid/verify"
        req = {'hfid': session['hfid']}
        r = rq.post(url, json=req)
        if r.response == 'OK':
            session['verified'] = str(dt.timestamp(dt.now()))
        else:
            return redirect(url_for('logout'))

@app.route('/')
def index():
    if 'hfid' not in session:
        return render_template('index_not_logged.html', title = app_name)
    else:
        return render_template('index_logged.html', title = app_name, user_name = session['user_name'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        req = {'email': email, 'password': password}
        url = HFurl + "/hfid/login"

        bytes = rq.post(url, json=req).content
        string = bytes.decode()
        r = json.loads(string)
        
        if r['response'] != "NO":
            session['hfid'] = r.response
            req = {'HFid': r.response}
            url = HFurl + "/hfid/info"
            
            r = json.loads(rq.post(url, json=req).content.decode())
            
            session['user_name'] = r['response']['name']
            return redirect(url_for('index'))
        else:
            return flash('Invalid email or password')
    else:
        return render_template('login.html', title = app_name)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        birthday = request.form['birthday']
        print(birthday)
        
        req = {'username': username, 'password': password, 'email': email, 'birthday': birthday}
        url = HFurl + "/hfid/register"
        
        r = rq.post(url, json=req)
        req = {'email': email, 'password': password}
        url = HFurl + "/hfid/login"
        
        r = json.loads(rq.post(url, json=req).content.decode())
        
        session['hfid'] = r['response']
        session['verified'] = str(dt.timestamp(dt.now()))

        req = {'HFid': r['response']}
        url = HFurl + "/hfid/info"

        r = json.loads(rq.post(url, json=req).content.decode())
        
        session['user_name'] = r['response']['name']

        return redirect(url_for('index'))
    return render_template('register.html', title = app_name)

@app.route('/logout')
def logout():
    session.pop('hfid', None)
    session.pop('user_name', None)
    session.pop('verified', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('FileNotFound.html', title = app_name), 404

if __name__ == '__main__':
    app.run(debug=True)