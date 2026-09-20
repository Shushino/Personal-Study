let firstCard = 10
let secondCard = 4
let thirdCard = 11
let cards = []
let sum = 0
let hasBlackJack = false
let isAlive = true
let message = ("")
let messageEl = document.getElementById("message-el")
let sumEl = document.querySelector("#sum-el")
let cardsEl = document.querySelector("#cards-el")

function startGame()
{
    cards = [firstCard, secondCard]
    sum = firstCard + secondCard
    hasBlackJack = false
    isAlive = true
    renderGame()
}

function renderGame()
{
    if (sum <= 20) {
        message = ("Do you want to draw a new card?")
    } else if (sum === 21) {
        message = ("You've got Blackjack!")
        hasBlackJack = true
    } else {
        message = ("You're out of the game!")
        isAlive = false
    }
    messageEl.textContent = message
    sumEl.textContent = "Sum: " + sum
    cardsEl.textContent = "Cards: " + cards.join(" ")
}

function newCard()
{
    if (isAlive && !hasBlackJack) {
        cards.push(thirdCard)
        sum += thirdCard
        renderGame()
    }
}