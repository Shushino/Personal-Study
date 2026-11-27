const stockNameEl = document.getElementById("stock-name")
const stockSymbolEl = document.getElementById("stock-symbol")
const stockPriceEl = document.getElementById("stock-price")
const stockTimeEl = document.getElementById("stock-time")
const priceTrendEl = document.getElementById("price-trend")

let currentPriceInCents = 99
let previousPrice = null
let hasGeneratedInitialPrice = false

function getFreshStockData() {
    if (hasGeneratedInitialPrice) {
        const changeInCents = Math.floor(Math.random() * 5) - 2
        currentPriceInCents = Math.max(1, currentPriceInCents + changeInCents)
    } else {
        hasGeneratedInitialPrice = true
    }

    return {
        name: "QtechAI",
        symbol: "QTA",
        price: currentPriceInCents / 100,
        time: new Date()
    }
}

function renderStockTicker(stock) {
    stockNameEl.textContent = stock.name
    stockSymbolEl.textContent = stock.symbol
    stockPriceEl.textContent = `$${stock.price.toFixed(2)}`
    stockTimeEl.dateTime = stock.time.toISOString()
    stockTimeEl.textContent = stock.time.toLocaleTimeString()

    if (previousPrice === null || stock.price === previousPrice) {
        priceTrendEl.textContent = "▶"
        priceTrendEl.className = "price-trend unchanged"
        priceTrendEl.setAttribute("aria-label", "No change")
    } else if (stock.price > previousPrice) {
        priceTrendEl.textContent = "▲"
        priceTrendEl.className = "price-trend up"
        priceTrendEl.setAttribute("aria-label", "Price increased")
    } else {
        priceTrendEl.textContent = "▼"
        priceTrendEl.className = "price-trend down"
        priceTrendEl.setAttribute("aria-label", "Price decreased")
    }

    previousPrice = stock.price
}

function updateStockTicker() {
    renderStockTicker(getFreshStockData())
}

updateStockTicker()
setInterval(updateStockTicker, 1500)
