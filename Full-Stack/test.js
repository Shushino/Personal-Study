const inputEl = document.getElementById("input-el");
const convertButton = document.getElementById("btn");
const lengthResult = document.getElementById("length");
const volumeResult = document.getElementById("volume");
const massResult = document.getElementById("mass");

convertButton.addEventListener("click", function() {
    const inputValue = inputEl.valueAsNumber;
    if (!Number.isFinite(inputValue)) {
        alert("Please enter a valid number.");
        return;
    }

    const metersToFeet = inputValue * 3.2808;
    const feetToMeters = inputValue * 0.3048;
    const litersToGallons = inputValue * 0.2642;
    const gallonsToLiters = inputValue * 3.7854;
    const kilogramsToPounds = inputValue * 2.2046;
    const poundsToKilograms = inputValue * 0.4536;

    lengthResult.textContent =
        `${inputValue} meters = ${metersToFeet.toFixed(3)} feet | ${inputValue} feet = ${feetToMeters.toFixed(3)} meters`;
    volumeResult.textContent =
        `${inputValue} liters = ${litersToGallons.toFixed(3)} gallons | ${inputValue} gallons = ${gallonsToLiters.toFixed(3)} liters`;
    massResult.textContent =
        `${inputValue} kilos = ${kilogramsToPounds.toFixed(3)} pounds | ${inputValue} pounds = ${poundsToKilograms.toFixed(3)} kilos`;
});