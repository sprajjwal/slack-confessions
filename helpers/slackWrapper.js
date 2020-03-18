const Confession = require('../models/confessions')
const fetch = require('node-fetch')

let client_id = "922216111702.957655129107" //process.env.SLACK_CLIENT_ID
let client_secret = "67eca442d1c5600f4f1991c7f362875e" //process.env.SLACK_CLIENT_SECRET


async function list_channels(access_token) {
  let r = await fetch(`https://slack.com/api/channels.list?token=${access_token}`)
  let c = await r.json()
  let channels = {}
  for (channel of c.channels) {
    channels[channel.name] = channel.id
  }
  return channels
}

async function post_to_channel(team_id, message){
  // Send a message to a channel
  const team = await Confession.findOne({'team_id': team_id})
  const token = team.bot_access_token
  const path_to_call = `http://slack.com/api/chat.postMessage?token=${token}&channel=${team.post_to}&text=${message}`;
  fetch(path_to_call)
}

async function get_im_channels(bot_token, bot_id) {
  /*DONT CALL: THIS IS A HELPER METHOD
    helper method used to find all the message channels*/
  const uri = `https://slack.com/api/users.conversations?token=${bot_token}&types=im&user=${bot_id}`
  const response = await fetch(uri)
  const data = await response.json()
  const im_channels = []
  for (channel of data.channels) {
    if (channel["user"] != 'USLACKBOT') {
      console.log("User is: ", channel.user, " at:  ", channel.id)
      im_channels.push(channel["id"]);}
  }
  return im_channels
}

async function get_messages_from_channel(bot_access_token, channel, ts=0) {
  /*DONT CALL: THIS IS A HELPER METHOD
    get's every message sent to the bot and updates the confessions
    database*/
  const uri = `https://slack.com/api/conversations.history?token=${bot_access_token}&channel=${channel}&oldest=${ts}`
  const response = await fetch(uri)
  const data = await response.json()
  
  let messages = []
  if(data.messages.length === 0) {
    return null
  }
  for (msg of data.messages) {
    if (msg.text !== null) {
      messages.unshift({
        ts: msg.ts,
        body: msg.text,
        posted: false,
        approved: false,
        denied: false
      })
    }
  }
  return messages
}

async function update_db(team_id) {
  // Gets new messages to be added to messages DB
  const team = await Confession.findOne({team_id})
  const im_channels = await get_im_channels(team.bot_access_token, team.bot_id)

  for (c of im_channels) {
    let msgs = []
    if (team.im_channels[c] === undefined) {
      msgs = await get_messages_from_channel(team.bot_access_token, c)
    } else {
      msgs = await get_messages_from_channel(team.bot_access_token, c, team.im_channels[c])
    }

    if (msgs !== null && msgs.length !== 0) {
      Confession.findOneAndUpdate({team_id},
        {$push: {"messages": msgs}},
        function(err, model) {
          if (err) console.log(err);
        }
      )
      team.im_channels[c] = msgs.slice(-1)[0].ts
      team.markModified("im_channels") // marks im_channels for modification
    }
  }
  await team.save()
  // console.log("-----------channels",team.im_channels)
  return true
}

async function get_mesaage(team_id) {
  /*gets an approved message from the database to post on slack,
    update it's posted to True.
    Returns False if there are no approved confess*/
  const team = await Confession.findOne({team_id})
  for (i in team.messages) {
    const m = team.messages[i]
    if (m.approved && !m.posted && !m.denied) {
      team.messages[i].posted = true
      team.markModified("messages")
      team.save()
      return m['body']
    }
  }
  return false
}
module.exports = {list_channels, post_to_channel,update_db, get_mesaage}