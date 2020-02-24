import os
import json
import slack
import requests
from pymongo import MongoClient

client_id =  os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]

"""
    This file handles the confessions stored in MongDB. 
    The connfessions object has the following model:

    confessions = {
        'team_id': str,
        'bot_id': str,
        'access_token': str,
        'bot_access_token': str,
        'team_name': str,
        'post_channels': ['str'], # all available channels
        'post_to': str,
        'im_channels': {
            'channel': ts,
        }
        'messages'= [
            {
                ts: timestamp,
                'body': str,
                'posted': bool,
                'approved': bool,
                'denied': bool
            }
        ]
        
    }

"""

def finish_auth(db, auth_code, post_to='random'):
    """ finishes authenticating with slack and handles response 
        Returns True if successfully added or False if it 
        already exists in db.
    """
    # An empty string is a valid token for this request
    client = slack.WebClient(token="")

    # Request the auth tokens from Slack
    response = client.oauth_access(
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )
    team_id = response['team_id'] # set team id

    if db.find_one({'team_id': team_id}):
        return False
    else:
        bot_id = response['bot']['bot_user_id'] # set bot id
        team_name = response['team_name'] # grab team name
        access_token = response['access_token'] # set access token
        bot_token = response['bot']['bot_access_token'] # set bot access token
        post_channel = list_channels(access_token, team_id) # set the channel name we post in
        team = {
            'team_id': team_id,
            'bot_id': bot_id,
            'access_token': access_token,
            'bot_access_token' : bot_token,
            'team_name': team_name,
            'post_channels': post_channel,
            'im_channels': {},
            'post_to': 'random',
            'messages': [],
        }
        db.insert_one(team)
        update_db(db, team_id)
        return team_id


def post_to_channel(db, team_id, message):
    """ Send a message to a channel"""
    team = db.find_one({'team_id': team_id})
    requests.post('https://slack.com/api/chat.postMessage', {
        'token': team['bot_access_token'],
        'channel': team['post_to'],
        'text': message,
        'username': "Slack-confessions",
    }).json()

def list_channels(access_token, team_id):
    """ lists all the available channels """
    res = requests.get('https://slack.com/api/channels.list', {'token': access_token}).json()
    channels = {channel["name"]: channel["id"] for channel in res["channels"]}
    return channels

def get_im_channels(bot_token, bot_id):
    """ DONT CALL: THIS IS A HELPER METHOD
    helper method used to find all the message channels"""
    res = requests.get('https://slack.com/api/users.conversations', {
        'token': bot_token,
        'types' : 'im',
        'user': bot_id
    }).json()
    im_channels = []
    for channel in res['channels']:
        if channel["user"] != 'USLACKBOT':
            im_channels.append(channel["id"])
    return im_channels

def get_messages_from_channel(bot_access_token, channel, ts=0):
    """ DONT CALL: THIS IS A HELPER METHOD
    get's every message sent to the bot and updates the confessions
    database"""
    res = requests.get('https://slack.com/api/conversations.history', {
        'token': bot_access_token,
        'channel': channel,
        'oldest': ts
    }).json()
    messages = []
    if len(res['messages']) == 0:
        return None
    for msg in res['messages']:
        if msg['text']:
            messages = [{
            'ts': msg['ts'],
            'body': msg['text'],
            'posted': False,
            'approved': False,
            'denied': False
            }] + messages
    return messages

def update_db(db, team_id):
    """ Gets new messages to be added to messages DB"""
    team = db.find_one({'team_id': team_id})
    im_channels = get_im_channels(team['bot_access_token'], team['bot_id'])

    for c in im_channels:
        if c not in team["im_channels"]:
            msgs = get_messages_from_channel(team['bot_access_token'], c, 0)
        else:
            msgs = get_messages_from_channel(team['bot_access_token'], c, team["im_channels"][c])
        if msgs is not None:
            team["messages"] += msgs
            if msgs:
                team['im_channels'][c] = msgs[len(msgs)-1]['ts']
    db.update_one({
        'team_id': team['team_id']
    }, {
        "$set": team
    })

def get_message(db, team_id):
    """ gets an approved message from the database to post on slack,
    update it's posted to True.
    Returns False if there are no approved confess"""
    team = db.find_one({'team_id': team_id})
    for i in range(len(team["messages"]) - 1):
        m = team["messages"][i]
        if m["approved"] and m['posted'] == False and m['denied'] == False:
            team["messages"][i]['posted'] = True
            db.update_one({
                'team_id': team['team_id']
            }, {
                "$set": team
            })
            return m['body']
    return False