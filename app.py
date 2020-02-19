from flask import Flask, flash, redirect, render_template, request
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
db = client.get_default_database()

users = db.users
confessions = db.confessions

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

@app.route('/register/<team_id>')
def get(team_id):
    return render_template('register.html', team_id=team_id)

@app.route('/register/<team_id>', methods=["POST"])
def register(team_id):
    """Register to start writing/posting confessions"""
    temp_code = request.form.get('password')
    room_code = temp_lobby_name + "^" + temp_code
    
    new_lobby = {
        'team_id': team_id,
        'password': temp_code
    }
    user.insert_one(new_lobby)
    return redirect(url_for('admin', lobby_code=room_code))

@app.route('/begin_auth')
def begin_auth():
    return redirect(f"https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }&redirect_uri={network}/finish_auth")

@app.route('/finish_auth', methods=["GET", "POST"])
def post_install():
    # Retrieve the auth code from the request params
    auth_code = request.args['code']
    team_id = finish_auth(confessions, auth_code)
    if not team_id:
        return redirect('/')
    else:
        return redirect(url_for('register', team_id=team_id))

@app.route('/login', methods=["GET", "POST"])
def login():
    """Login to the web app"""
    if request.method == "GET":
        return render_template('login.html')
    
    if request.method == "POST":
        team_id = request.args.get('team_id')
        password = request.args.get('password')
        
        user = users.find_one({'team_id': team_id, 'password': password})
        if user:
            code = f"{team_id}^{password}"
            return redirect(url_for('authentication',code=code))
        else:
            return redirect(url_for('login', message='incorrect credentials'))

@app.route('/admin/<code>')
def authentication(code):
    [team_id, password] = code.split("^", 1)
    room = users.find_one({'team_id': team_id, 'password': password})
    if room:
        confession = confessions.find_one({'team_id':team_id})
        return render_template('admin.html', messages=confession["messages"])
    else:
        return redirect(url_for('login', message='incorrect credentials'))

@app.route('/admin/<code>', methods=['POST'])
def post_confessions(code):
    # make sure to check form for different format
    form = request.form.list
    [team_id, password] = code.split("^", 1)
    room = users.find_one({'team_id': team_id, 'password': password})
    pass

@app.route('/admin/<code>/settings', methods=['GET','POST'])
def settings(code):
    if methods == 'GET':
        return render_template('settings.html')

    if methods == 'POST':
        pass

@app.route("/logout")
def logout():
    """Log out of the workspace confession page"""
    # session['logged_in'] = False
    return redirect('/')


"""
@app.route('/auth')
def setup():
    # authentication, adding app to slack, writing data to db happens here
    return 'Hello, world'
"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))