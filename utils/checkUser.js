const User = require("../models/users");
const jwt = require('jsonwebtoken')

const checkUser = (req, res, next) => {
  console.log("Checking authentication");

  if (typeof req.cookies.pToken === "undefined" || req.cookies.pToken === null) {
    req.user = null;
    console.log("nothing found")
  } else {
    var token = req.cookies.pToken;
    var decodedToken = jwt.decode(token, { complete: true }) || {};
    req.user = decodedToken.payload;
    console.log("user set")
  }
  next();
};


module.exports = checkUser;