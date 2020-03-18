const jwt = require('jsonwebtoken')
const User = require('../models/users')
const Confession = require('../models/confessions')

module.exports = (app) => {

  // Admin page update 
  app.post('/register/:team_id', (req, res) => {
    const team_id = req.params.team_id
    Confession.findOne({team_id})
      .then(confession => {
        if (confession === null) {
          console.log("Confession doesn't exist!")
          return res.redirect('/')
        } else {
          User.findOne({team_id})
            .then(user => {
              if (user === null) {
                const password = req.body.password
                let new_user = new User()
                new_user.team_id = team_id
                new_user.password = password
                new_user.save()
                .then (success => {
                  console.log(success)
                  return res.redirect('/admin')
                })
                .catch(err => {console.log(err)})
              } else {
                console.log("user already exists")
                return res.redirect('/')
              }
            })
        }
      })
  })

  // LOGIN form
  app.get('/login', (req, res) => {
    res.render('login')
  })

  // LOGIN POST
  app.post('/login', (req, res) => {
    const team_id = req.body.team_id;
    const password = req.body.password;


    User.findOne({ team_id}, "team_id password")
    .then(user => {
      if (!user ) {
        // User not found
        return res.render('login', {errorMsg: "Incorrect Login"})
      }
      // Check the password
      user.comparePassword(password, (err, isMatch) => {
        if (!isMatch) {
          // Password does not match
          return res.render('login', {errorMsg: "Incorrect Login"})
        }
        // Create a token
        const token = jwt.sign({ _id: user._id, team_id: user.team_id }, process.env.SECRET, {
          expiresIn: "60 days"
        });
        // Set a cookie and redirect to root
        res.cookie("pToken", token, { maxAge: 900000, httpOnly: true });
        return res.redirect('/admin')
      });
    })
    .catch(err => {
      console.log(err);
      return res.render('login', {errorMsg: "Incorrect Login"})
    });
  });
  
  // LOGOUT
  app.get('/logout', (req, res) => {
    res.clearCookie('slToken');
    res.redirect('/');
})
}