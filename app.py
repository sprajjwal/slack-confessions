from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

"""
client = MongoClient()
db = client.slack-confessions
"""
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/slack-confessions')
client = MongoClient(host=f'{host}?retryWrites=false')

app = Flask(__name__)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))