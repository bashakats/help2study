let tokenErrorDialog = document.getElementById('thankYouDialog')
function showDialog() {
    tokenErrorDialog.classList.remove('visually-hidden')
}


function hideDialog() {
    window.location.assign(redirectUrl)
}
