let count = 0
let SaveEl =document.getElementById("save-el") 
function increment()
{
    count += 1
    document.getElementById("count-el").innerText = count
}

function save()
{
    let countStr = count + " - "
    SaveEl.textContent += countStr
    count = 0
    document.getElementById("count-el").innerText = count
    
}