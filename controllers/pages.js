const jwt = require('jsonwebtoken')
const User = require('../models/users')
const request = require('request')

const Confession = require("../models/confessions")

const {list_channels, post_to_channel, update_db, get_mesaage} = require('../helpers/slackWrapper')

const client_id = "922216111702.957655129107" //process.env.SLACK_CLIENT_ID
const client_secret = "67eca442d1c5600f4f1991c7f362875e" //process.env.SLACK_CLIENT_SECRET
const oauth_scope = 'bot, channels:read, chat:write:bot, im:read, im:history' 
// const network = "https://slack-confessions.herokuapp.com"
const network = "http://127.0.0.1:3000"

module.exports = (app) => {

  // start of authentication
  app.get('/begin_auth', (req, res) => {
    return res.redirect(`https://slack.com/oauth/authorize?scope=${ oauth_scope }&client_id=${ client_id }&redirect_uri=${network}/finish_auth`)
  })

  // redirect from slack api oauth
  app.get('/finish_auth', async (req, res) => {
    const auth_code = req.query.code
    let state = req.query.state;

    // An empty string is a valid token for this request
    const options = {
      uri: 'https://slack.com/api/oauth.access?code='
          +auth_code+
          '&client_id='+client_id+
          '&client_secret='+client_secret+
          '&redirect_uri='+'http://127.0.0.1:3000/finish_auth',
      method: 'GET'
    }

    request(options, (error, response, body) => {
      const JSONresponse = JSON.parse(body)
      if (!JSONresponse.ok){
          console.log('__________no resp',JSONresponse)
          return res.redirect('/')
      }else{
        const response = JSONresponse
        const team_id = response.team_id
        Confession.findOne({team_id: team_id})
          .then(async function(found) {
            if (found === null) {
              const bot_id = response['bot']['bot_user_id'] // set bot id
              const team_name = response['team_name'] // grab team name
              const access_token = response['access_token'] // set access token
              const bot_token = response['bot']['bot_access_token'] // set bot access token
              let post_channel = await list_channels(access_token)
              let team = new Confession()
              team.team_id= team_id,
              team.bot_id= bot_id,
              team.access_token= access_token,
              team.bot_access_token = bot_token,
              team.team_name= team_name,
              team.post_channels= post_channel,
              team.im_channels= {},
              team.post_to= 'random',
              team.messages= [],             
              team.save()
              .then(team => {return res.render('register', {team_id})})
              .catch(err => {
                console.log("____________team save",err)
                return res.redirect('/')
              })
            } else {
              return res.redirect('/')
            } 
          })
          .catch(err => {
            console.log(err)
          })
      }
    })
  })


  app.get('/admin', async (req, res) => {
    const user = req.user
    if (user !== null) {
      const confession = await Confession.findOne({team_id: user.team_id})
      // const team = await Confession.findOne({team_id: "TT46C39LN"})
      // console.log(team)
      const messages = confession.messages
      return res.render('admin', {messages})
    } else {
      return res.redirect('/login')
    }
    
  })
}