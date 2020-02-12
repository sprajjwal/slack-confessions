from flask import Flask, flash, redirect, render_template, request, session, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from helpers.slackWrapper import *
from apscheduler.schedulers.background import BackgroundScheduler

"""
client = MongoClient()
db = client.slack-confessions
"""
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/slack-confessions')
client = MongoClient(host=f'{host}?retryWrites=false')

# class object initialization
app = Flask(__name__)

# edit this function for job scheduling
def scheduled_jobs():
    print('I am working...')

# Task Scheduler
scheduler = BackgroundScheduler()
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    job = scheduler.add_job(scheduled_jobs, 'interval', minutes=1) #set minutes here
scheduler.start()

# notes:
# Add this a tag for add to slack: <a href=f"https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }&redirect_uri={network}/finish_auth">Add to Slack</a>

@app.route('/')
def index():
    """Return homepage"""
    return render_template('index.html')

@app.route('/register')
def register():
    return register()

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
        #return index()  

@app.route('/admin')
@login_required
def admin():
    """Admin page to post confession (User)"""
    return admin()

@app.route('/begin_auth')
@login_required
def begin_auth():
    return redirect(f"https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }&redirect_uri={network}/finish_auth")

@app.route('/admin/<team_id>')
@login_required
def approve_or_deny():
    return admin()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

"""
@app.route('/auth')
def setup():
    # authentication, adding app to slack, writing data to db happens here
    return 'Hello, world'
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))