const express = require('express')
const app = express()
const port = 3000
require('dotenv').config();
const path = require('path')

const handlebars = require('express-handlebars')
  .create({
    defaultLayout: 'main',
    helpers: {
        section: function (name, options) {
            if (!this._sections) {
                this._sections = {};
            }
            this._sections[name] = options.fn(this);
            return null;
        }
    }
  });

app.engine('handlebars', handlebars.engine);
app.set('view engine', 'handlebars');


const bodyParser = require('body-parser');
const expressValidator = require('express-validator');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const checkUser = require("./utils/checkUser")


// Use Body Parser
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));





// Handlebars
// app.engine('handlebars', exphbs({ defaultLayout: 'main' }));


app.use(express.static("public")); // enables supplying static files

// Add after body parser initialization!
// app.use(expressValidator());

// enable JWT
app.use(cookieParser());

// setup user auth
app.use(checkUser);


require('./data/confessions-db');

// import routes
require("./controllers/auth")(app);
require("./controllers/pages")(app);

// app.get('/', (req, res) => res.render('posts-index'))
app.get('/', (req, res) => res.render('index'))

app.listen(port, () => console.log(`Example app listening on port ${port}!`))



module.exports = app;