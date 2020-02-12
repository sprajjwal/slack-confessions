from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
# from slack/slackWrapper import mySlack

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
# scheduler = BackgroundScheduler()
# if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#     job = scheduler.add_job(scheduled_jobs, 'interval', minutes=1) #set minutes here
# scheduler.start()

# notes:
# Add this a tag for add to slack: <a href=f"https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }&redirect_uri={network}/finish_auth">Add to Slack</a>

@app.route('/')
def index():
    """Return homepage"""
    # search_workspace = request.query.filter_by(list_channels)
    return render_template('index.html')

# @app.route('/results', method=['GET', 'POST'])
# def search():
#     """Search for specific workspace on Slack"""
#     results = []
#     search_string = search.data['search']

#     if not results:
#         # flash('No results found')
#         return redirect('/')
#     else: # display search results
#         return render_template('results.html', results=results)
#     pass

@app.route('/admin')
def admin():
    """Admin page to post confession (User)"""
    return 'Hello, world'

@app.route('/auth')
def setup():
    """ authentication, adding app to slack, writing data to db happens here"""
    return 'Hello, world'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))