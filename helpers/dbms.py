from pymongo import MongoClient


"""
    This file handles the confessions stored in MongDB. 
    The connfessions object has the following model:

    confessions = {
        'channel_id' = str,
        'ts' = timestamp,
        'messages'= [{
            timestamp: {
                'body': string message,
                'posted': bool,
                'approved': bool
            }},
            {}
        ]
    }

    messages = [{
        'ts': message['ts'],
        'body': message['text'],
        'posted': False,
        'approved': 'none'
        },
        {}
    ]

"""

def get_ts(messages):
    max_ts = 0
    for msg in messages:
        if msg['ts'] > max_ts:
            max_ts = msg['ts']
    return max_ts

def add_channel(db, channel_id, messages):
    """ Adds a new channel document in the database """
    if (not db.find_one({'channel_id': channel_id})):
        confessions = {
            'channel_id' = channel_id,
            'ts' = get_ts(messages),
            'messages' = messages
        }
        db.insert_one(confessions)
    else:
        add_confessions(db, channel_id, messages)

def add_confession(db, channel_id, messages):
    """ Adds new confessions to a channel document in the database"""
    confession = db.find_one({'channel_id': channel_id})
    confession['ts'] = get_ts(messages)
    for ts in messages:
        if not ts in confession['messages']:
            confession['messages'][ts] = messages[ts]
    db.update_one(
        {"channel_id": channel_id},
        {'$set': confession}
    )

def get_message(db, channel_id):
    """ gets an approved message from the database for a given channel and
    delete it from place"""
    confession = db.find_one({'channel_id': channel_id})
    confess = None
    for i in range(len(confession['messages'])):
        if confession['messages'][i]['approved'] == False:
            del confession['messages'][i]
        elif confession['messages'][i]['approved']:
            if not confession['messages'][i]['posted'] == False:
                confess = confession['messages'].pop(i)
        
    db.update_one(
        {"channel_id": channel_id},
        {'$set': confession}
    )
    return confess




    