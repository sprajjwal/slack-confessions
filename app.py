from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from slack/slackWrapper import mySlack

"""
client = MongoClient()
db = client.slack-confessions
"""
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/slack-confessions')
client = MongoClient(host=f'{host}?retryWrites=false')

# class object initialization
app = Flask(__name__)
slackWrapper = mySlack()


# check for token and set it:
token = ""
# open token.json and load access token
try:
    with open('./token.json', 'r') as f:
        slackWrapper.set_token(json.load(f)['access_token']) #set access token in the object
except:
    print("no tokens found")

# notes:
# Add this a tag for add to slack: <a href=f"https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }&redirect_uri={network}/finish_auth">Add to Slack</a>

@app.route('/')
def index():
    """Return homepage"""
    return render_template('index.html')

@app.route('/search', method=['GET', 'POST'])
def search():
    """Search for specific workspace on Slack"""
    form = SearchForm()

@app.route('/admin')
def admin():


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))