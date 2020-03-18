const password1 = document.getElementById('password1')
const password2 = document.getElementById('password2')
const form = document.getElementById('main-form')
const errorMsg = document.getElementById('error-message')
const carrotKeyMsg = document.getElementById('carrot-message')

password1.addEventListener("input", function(e) {
  if (password1.value.includes("^")) {
    password1.value = ""
    carrotKeyMsg.style.display = 'block'
  } else {
    carrotKeyMsg.style.display = 'none'
  }
})

password2.addEventListener("change", function(e) {
  if (password1.value !== password2.value) {
    errorMsg.style.display = "block"
    password2.value = ""
  } else {
    errorMsg.style.display = "none"
  }
})

form.addEventListener("submit", function(e) {
  if (password1.value != "" && password1.value !== password2.value) {
    e.preventDefault()
  }
})