const mongoose = require("mongoose")
const Schema = mongoose.Schema;

const ConfessionSchema = new Schema({
  team_id: {type: String, unique: true, required: true},
  bot_id: { type: String},
  access_token: {type: String},
  bot_access_token: {type: String},
  post_channels: {type: Object},
  im_channels: {type: Object},
  post_to: {type: String, default: 'random'},
  messages: [{
    ts: {type: String},
    body: {type: String},
    posted: {type: Boolean, default: false},
    approved: {type: Boolean, default: false},
    denied: {type: Boolean, default: false}
  }]
}, { minimize: false })

module.exports = mongoose.model("Confession", ConfessionSchema)