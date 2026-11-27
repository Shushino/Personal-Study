export default function getMatchTripsArr(arr, keyword) {
    return arr.filter(function (trip) {
        return trip.description.toLowerCase().includes(keyword)
    })
}