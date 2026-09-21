let cards = []
let sum = 0
let hasBlackJack = false
let isAlive = true
let message = ("")
let messageEl = document.getElementById("message-el")
let sumEl = document.querySelector("#sum-el")
let cardsEl = document.querySelector("#cards-el")

function getRandomCard()
{
    let randomNumber = Math.floor(Math.random() * 13) + 1

    if (randomNumber === 1) {
        return 11
    } else if (randomNumber >= 11) {
        return 10
    }

    return randomNumber
}

function startGame()
{
    cards = [getRandomCard(), getRandomCard()]
    sum = cards[0] + cards[1]
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
        let card = getRandomCard()
        cards.push(card)
        sum += card
        renderGame()
    }
}