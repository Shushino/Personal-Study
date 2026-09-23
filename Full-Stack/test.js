// let homeScore = 0
// let guestScore = 0

// function addHomePoints(points) {
//     homeScore += points
//     document.getElementById("home-score").textContent = homeScore
// }

// function addGuestPoints(points) {
//     guestScore += points
//     document.getElementById("guest-score").textContent = guestScore
// }

let age = 2026

if (age <= 5) {
    console.log("Free!")
} else if (age >= 6 && age < 17) {
    console.log("Child Discount")
} else if (age >= 18 && age < 26) {
    console.log("Student discount")
} else if (age >= 27 && age < 66) {
    console.log("Full price")
} else {
    console.log("Senior Citizen discount")
}