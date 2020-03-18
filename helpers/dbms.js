const Confession = require('../models/confessions')
const {get_message, post_to_channel} = require("./slackWrapper")

async function post_to_slack() {
  // Helper method that posts a confession to every workplace
  const all = await Confession.find({})
  for (workplace of all) {
    const msg  = await get_message(workplace.team_id)
    if (msg) {
      console.log("sending confession")
      post_to_channel(workplace.team_id, msg)
    }
  }
}

async function clear_denied() {
  // Helper method that removes all the denied confessions
  const all = await Confession.find({})
  for (workplace of all) {
    for (index in workplace.messages) {
      let m = workplace.messages[index]
      if (m.denied || (m.approved && m.posted)) {
        workplace.messages.splice(index) // CHECK IF THIS WORKS!!!!
      }
    }
    Confession.findOneAndUpdate({team_id},
      {$set: {"messages": workplace.messages}},
      function(err, model) {
        if (err) console.log(err);
      }
    )
  }
}

module.exports = {post_to_slack, clear_denied}