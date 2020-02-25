from pymongo import MongoClient
from .slackWrapper import get_message, post_to_channel

def post_to_slack(db):
  """ Helper method that posts a confession to every workplace"""
  all = db.find({})
  for workplace in all:
    msg = get_message(db, workplace['team_id'])
    if msg:
      print("Sending confessions")
      post_to_channel(db, workplace['team_id'], msg)


def clear_denied(db):
  """ Helper method that removes all the denied confessions """
  print("Clearing denied items")
  all = db.find({})
  for workplace in all:
    for index in range(len(workplace['messages']) - 1):
      if workplace['messages'][index]['denied'] or workplace['messages'][index]['posted']:
        del workplace['messages'][index]
    db.update_one({
        'team_id': workplace['team_id']
    }, {
        "$set": workplace
    })