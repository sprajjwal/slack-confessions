from flask import Flask, flash, redirect, render_template, request, jsonify,url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from helpers.slackWrapper import *


"""
client = MongoClient()
"""

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/slack-confessions')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()

users = db.users
confessions = db.confessions

app = Flask(__name__)

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = 'bot, channels:read, chat:write:bot, im:read, im:history' #os.environ["SLACK_BOT_SCOPE"]
network = "https://slack-confessions.herokuapp.com"

# notes:
# Add this a tag for add to slack: <a href=f"https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }&redirect_uri={network}/finish_auth">Add to Slack</a>

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
        return register_team(team_id)

@app.route('/')
def index():
    """Return homepage"""
    return render_template('index.html')


def register_team(team_id):
    return render_template('register.html', team_id=team_id)

@app.route('/register/<team_id>', methods=["POST"])
def register(team_id):
    """Register to start writing/posting confessions"""
    temp_code = request.form.get('password')
    room_code = team_id + "^" + temp_code
    
    confession = confessions.find_one({'team_id': team_id})

    if confession:
        new_lobby = {
            'team_id': team_id,
            'password': temp_code
        }
        users.insert_one(new_lobby)
        return redirect(url_for('authentication', code=room_code))
    else:
        return redirect()

@app.route('/login', methods=["GET", "POST"])
def login():
    """Login to the web app"""
    if request.method == "GET":
        return render_template('login.html')
    
    if request.method == "POST":
        team_id = request.form.get('team_id')
        password = request.form.get('password')
        user = users.find_one({'team_id': team_id, 'password': password})
        if user:
            code = f"{team_id}^{password}"
            return redirect(url_for('authentication',code=code))
        else:
            return redirect(url_for('login', message='incorrect credentials'))

@app.route('/admin/<code>')
def authentication(code):
    [team_id, password] = code.split("^", 1)
    update_db(confessions, team_id)
    room = users.find_one({'team_id': team_id, 'password': password})
    if room:
        confession = confessions.find_one({'team_id':team_id})
        return render_template('admin.html', messages=confession["messages"], code=code)
    else:
        return redirect(url_for('login', message='incorrect credentials'))

@app.route('/admin/<code>', methods=['POST'])
def post_confessions(code):
    # make sure to check form for different format
    form = request.form.to_dict()
    [team_id, password] = code.split("^", 1)
    room = users.find_one({'team_id': team_id, 'password': password})
    d = {"approved": "denied", "denied": "approved"}
    if room:
        lis = []
        confession = confessions.find_one({'team_id':team_id})
        for i in range(len(confession['messages'])):
            if f'opt-{i}' in form:
                confession['messages'][i][form[f'opt-{i}']] = True
                confession['messages'][i][d[form[f'opt-{i}']]] = False
        confessions.update_one({
            'team_id': team_id
        }, {
            "$set": confession
        })
        return redirect(url_for('authentication', code=code))
    else:
        return redirect(url_for('login', message='incorrect credentials'))

@app.route('/admin/<code>/settings', methods=['GET','POST'])
def settings(code):
    [team_id, password] = code.split("^", 1)
    
    room = users.find_one({'team_id': team_id, 'password': password})
    if room:
        if request.method == 'GET':
            confession = confessions.find_one({'team_id':team_id})
            team = {
                'team_name': confession['team_name'],
                'team_id': team_id,
                'post_to': confession['post_channels'].keys()
            }
            return render_template('settings.html', team=team, code=code)

        if request.method == 'POST':
            return
            form = request.form.to_dict()
            room['password'] = form['new_password']
            users.update_one({
                'team_id': team_id
            }, {
                "$set": confession
            })
            confession['post_to'] = form['post_select']
            confessions.update_one({
                'team_id': team_id
            }, {
                "$set": confession
            })
            return redirect('/')
    else:
        # make error.html
        return redirect('/')

@app.route("/logout")
def logout():
    """Log out of the workspace confession page"""
    # session['logged_in'] = False
    return redirect('/')




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))