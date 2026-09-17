let homeScore = 0
let guestScore = 0

function addHomePoints(points) {
    homeScore += points
    document.getElementById("home-score").textContent = homeScore
}

function addGuestPoints(points) {
    guestScore += points
    document.getElementById("guest-score").textContent = guestScore
}