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




const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=<>?";

function generatePassword() {
    let password = "";
    for (let i = 0; i < 15; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        password += characters[randomIndex];
    }
    return password;
}

const firstPassword = generatePassword();
const secondPassword = generatePassword();

console.log("First password:", firstPassword);
console.log("Second password:", secondPassword);
