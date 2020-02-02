import os
import json
import slack
import requests

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = 'bot, channels:read, chat:write:bot' #os.environ["SLACK_BOT_SCOPE"]


class mySlack:
    
    def finish_auth(self, auth_code):
        """ finishes authenticating with slack and handles response """
        # An empty string is a valid token for this request
        self.client = slack.WebClient(token="")

        # Request the auth tokens from Slack
        self.response = self.client.oauth_access(
            client_id=client_id,
            client_secret=client_secret,
            code=auth_code
        )

        # set bot id
        self.bot_id = self.response['bot']['bot_user_id']
        # set team id
        self.team_id = self.response['team_id']
        # set access token
        self.access_token = self.response['access_token']


    def post_to_channel(self, channel_id, message, user_id):
        """ Send a message to a channel"""
        requests.post('https://slack.com/api/chat.postMessage', {
            'token': self.access_token,
            'channel': channel_id,
            'text': message,
            'username': "Slack-confessions",
        }).json()

    def list_channels(self):
        """ lists all the available channels """
        res = requests.get('https://slack.com/api/channels.list', {'token': self.access_token}).json()
        self.channels = {channel["name"]: channel["id"] for channel in res["channels"]}
        return self.channels
    
    def get_im_channel(self):
        """ helper method used to find the message channel"""
        res = requests.get('https://slack.com/api/conversations.list', {
            'token': 'self.access_token,
            'types' : 'im',
        }).json()

        # to make sure we get a response
        while not res['ok']:
            res = requests.get('https://slack.com/api/conversations.list', {
                'token' : self.access_token,
                'types' : 'im',
            }).json()
        
        for channel in res['channels']:
            if channel["user"] == self.bot_id:
                self.im_channel = channel["id"]
        return self.im_channel

    def get_messages(self, channel, oldest=0):
        """ get's every message sent to the bot """
        res = requests.get('https://slack.com/api/conversations.history', {
            'token': self.access_token,
            'channel': channel,
            'oldest': oldest
        }).json()
        ret_arr = {}
        print(res)
        for message in res['messages']:
            ret_arr[message['ts']] = message['text']
        return ret_arr
    