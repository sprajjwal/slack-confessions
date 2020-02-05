import os
import json
import slack
import requests
from pymongo import MongoClient



def finish_auth(auth_code, db, post_to='random'):
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

    
    bot_id = response['bot']['bot_user_id'] # set bot id
    team_id = response['team_id'] # set team id
    team_name = response['team_name'] # grab team name
    access_token = response['access_token'] # set access token
    im_channel = get_im_channel(access_token, bot_id) # set im channel for incoming bot messages
    post_channel = list_channels(access_token, post_to) # set the channel name we post in
    team = {
        'team_id': team_id,
        'bot_id': bot_id,
        'access_token': access_token,
        'team_name': team_name,
        'im_channel': im_channel,
        'post_channel': post_channel,
        'ts': 0
    }
    if db.find_one({'team_id': team_id}):
        return False
    else:
        db.insert_one(team)
        return True
    


def post_to_channel(db, team_id, message):
    """ Send a message to a channel"""
    team = db.find_one({'team_id': team_id})
    requests.post('https://slack.com/api/chat.postMessage', {
        'token': team['access_token'],
        'channel': team['post_channel'],
        'text': message,
        'username': "Slack-confessions",
    }).json()

def list_channels(db, team_id, channel_name=None):
    """ lists all the available channels """
    team = db.find_one({'team_id': team_id})
    res = requests.get('https://slack.com/api/channels.list', {'token': team[team_id]}).json()
    if channel_name:
        for channel in res["channels"]:
            if channel["name"] == channel_name:
                return channel["id"]
    channels = {channel["name"]: channel["id"] for channel in res["channels"]}
    return channels

def get_im_channel(access_token, bot_id):
    """ helper method used to find the message channel"""
    res = requests.get('https://slack.com/api/conversations.list', {
        'token': access_token,
        'types' : 'im',
    }).json()

    # to make sure we get a response
    while not res['ok']:
        res = requests.get('https://slack.com/api/conversations.list', {
            'token' : access_token,
            'types' : 'im',
        }).json()
    
    for channel in res['channels']:
        if channel["user"] == bot_id:
            im_channel = channel["id"]
    return im_channel

def get_messages(db, team_id):
    """ get's every message sent to the bot """
    team = db.find_one({'team_id': team_id})
    res = requests.get('https://slack.com/api/conversations.history', {
        'token': team['access_token'],
        'channel': team['im_channel'],
        'oldest': team['ts']
    }).json()
    db.update_one({
        'team_id': team_id
    }, {
        "$set": {
            "ts": res['messages'][0]['ts']
        }
    })
    messages = []
    for msg in res['messages']:
        messages.append({
            'ts': msg['ts'],
            'body': msg['text'],
            'posted': False,
            'approved': None
            })
    return messages
