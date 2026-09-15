let count = 0

function increment()
{
    count += 1
    document.getElementById("count-el").innerText = count
}

function save()
{
    document.getElementById("count-el").innerText = 0
}