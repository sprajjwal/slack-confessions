import os
import json
import requests


class mySlack:
    def set_token(self, token):
        """set access token if json file is available"""
        self.access_token = token
    
    def post_to_channel(self, channel_id, message, username="Slack-confessions"):
        """ Writes a message to given channel"""
        requests.post('https://slack.com/api/chat.postMessage', {
            'token': self.access_token,
            'channel': channel_id,
            'text': message,
            'username': username,
        }).json()

    def list_channels(self):
        """ list all the available channels """
        res = requests.get('https://slack.com/api/channels.list', {'token': self.access_token}).json()
        self.channels = {channel["name"]: channel["id"] for channel in res["channels"]}
        return self.channels
    