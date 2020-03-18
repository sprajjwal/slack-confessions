const username = document.getElementById("team_id")
const password = document.getElementById("password")
const form = document.getElementById("main-form")
const carrotKeyMsg = document.getElementById('carrot-message')

console.log("here")
password.addEventListener("input", function(e) {
  if (password.value.includes("^")) {
    password.value = ""
    carrotKeyMsg.style.display = 'block'
  } else {
    carrotKeyMsg.style.display = 'none'
  }
})


username.addEventListener("input", function(e) {
  if (username.value.includes("^")) {
    username.value = ""
    carrotKeyMsg.style.display = 'block'
  } else {
    carrotKeyMsg.style.display = 'none'
  }
})