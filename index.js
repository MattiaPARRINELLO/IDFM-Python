const loaderDiv = document.getElementById("loaderDiv");
async function getApiKey() {
    try {
        const response = await fetch("DataSet/apikey.json");
        let data = await response.json();
        data = data.APIKey;
        return data;
    } catch (error) {
        console.error("Error:", error);
        return null;
    }
}
const APIUrl = "https://prim.iledefrance-mobilites.fr/marketplace"


//Get stations data from city name, limit is the numer of results
//if no limit is set, all results are returned
//Is called when the page is loaded, when the user press enter in the input or when the user click on a suggestion
//return an array of objects
async function getStations(cityName, limit = 0) {
    try {
        const response = await fetch("DataSet/arrets.json");
        const stop = await response.json();
        const resultats = stop.filter(station => station.arrname.toLowerCase().includes(cityName.toLowerCase()));
        const exactMatch = resultats.filter(station => station.arrname.toLowerCase() === cityName.toLowerCase());
        // sort retults by % of match like when the querry is Argenteuil, the first one on result is Argenteuil and then Val d'Argenteuil
        resultats.sort((a, b) => {
            const aMatch = a.arrname.toLowerCase().indexOf(cityName.toLowerCase());
            const bMatch = b.arrname.toLowerCase().indexOf(cityName.toLowerCase());
            return aMatch - bMatch;
        });

        if (resultats.length <= 0) {
            console.error("No station found");
            loading(false)
            return null;
        }
        if (limit > 0) {
            return resultats.slice(0, limit);
        }
        return resultats;
    } catch (error) {
        console.error("Error:", error);
        return [];
    }
}


//Get line data from lineID, return an object
//Is called when a new station is requested
//return an object containing the line data
async function getLineData(lineID) { //lineID format : C02711 of STIF:Line::C02711:
    const simpleLineIDPattern = /^C\d{5}$/;
    const lineIDPattern = /^STIF:Line::C\d{5}:$/;
    if (!simpleLineIDPattern.test(lineID)) {
        if (!lineIDPattern.test(lineID)) {
            console.error("Invalid lineID format : ", lineID);
            return null;
        }
        // convert full lineID to simple lineID
        lineID = lineID.slice(11, 17);
    }
    try {
        const response = await fetch("DataSet/lignes.json");
        const linesData = await response.json();
        const resultats = linesData.filter(line => line.id_line === lineID);
        if (resultats[0].picto === null) {
            resultats[0].picto = {
                url: "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png",
                width: "100",
                height: "100",
                mimetype: "image/png"
            }
        }
        let returnData = {
            id: resultats[0].id_line || "unknown",
            name: resultats[0].name_line || "unknown",
            accentColor: resultats[0].colourweb_hexa,
            textColor: resultats[0].textcolourweb_hexa,
            image: {
                url: resultats[0].picto.url || "unknown",
                width: resultats[0].picto.width || "unknown",
                height: resultats[0].picto.height || "unknown",
                mimetype: resultats[0].picto.mimetype || "unknown"
            }
        }
        return returnData;


    } catch (error) {
        console.error("An error occured : ", error);
    }
}


//Call the api to get the next departures from a station
//Is called when a new station is requested
//return an unformatted object
async function getFutureTrainDepartures(stationID) { //stationID format : STIF:StopPoint:Q:41087: or 41087
    const fullStationIDPattern = /^STIF:StopPoint:Q:\d{5,6}:$/;
    if (!fullStationIDPattern.test(stationID)) {
        const shortStationIDPattern = /^\d{5,6}$/;
        if (!shortStationIDPattern.test(stationID)) {
            console.error("Invalid station ID format : ", stationID);
            return 'error';
        }
        stationID = `STIF:StopPoint:Q:${stationID}:`;
    }
    console.log("New station requested : ", stationID);
    const url = `${APIUrl}/stop-monitoring?MonitoringRef=${stationID}`
    let apiKey = await getApiKey();
    let response = await fetch(url, {
        headers: {
            'Accept': 'application/json',
            'apikey': apiKey
        }
    })
    response = await response.json()
    return response
}


//format the next departures data
//Is called after getFutureTrainDepartures
//return an array of objects (departures)
async function formatNextDepartures(data) { //data is the object returned by getFutureTrainDepartures
    let returnData = [];
    const mainData = data.Siri.ServiceDelivery.StopMonitoringDelivery[0].MonitoredStopVisit;
    let departureNum = 0;
    let departureNumEl = document.getElementById("loaderCounter")
    for (const info of mainData) {
        console.groupCollapsed("####---New Departure---####")
        departureNum++;
        departureNumEl.textContent = departureNum
        let isLive = true
        console.log(info.MonitoredVehicleJourney.LineRef.value)
        let lineData = await getLineData(info.MonitoredVehicleJourney.LineRef.value)
        let arrivalTemp = 0;
        // Set default value for ArrivalPlatformName if undefined
        if (!info.MonitoredVehicleJourney.MonitoredCall.ArrivalPlatformName) {
            info.MonitoredVehicleJourney.MonitoredCall.ArrivalPlatformName = { value: "#" };
        }

        // Determine the arrival time
        if (info.MonitoredVehicleJourney.MonitoredCall.ExpectedArrivalTime) {
            arrivalTemp = info.MonitoredVehicleJourney.MonitoredCall.ExpectedArrivalTime;
        } else {
            arrivalTemp = info.MonitoredVehicleJourney.MonitoredCall.AimedArrivalTime ||
                info.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime;
            isLive = false;
        }


        // If the train destination is the station itself, skip the train
        if (info.MonitoredVehicleJourney.DestinationName[0].value === info.MonitoredVehicleJourney.MonitoredCall.StopPointName[0].value) {
            console.log("---Skipping train---")
            console.log("Destination is the same as the station")
            console.log("##################")
            console.groupEnd()
            continue;
        }

        let arrival = new Date(arrivalTemp)
        let now = new Date()
        let diff = arrival - now
        if (diff < -120000 || diff > 3600000 || isNaN(diff)) {
            console.log("---Skipping train---")
            console.log("Train is too early or too late")
            console.log("##################")
            console.groupEnd()
            continue;
        }

        let diffMinutes = Math.floor(diff / 60000);
        let diffSeconds = Math.floor((diff % 60000) / 1000);
        diff = `${diffMinutes}m ${diffSeconds}s`;
        if (diff == "NaNm NaNs") {
            diff = "Unknown"

        }
        if (diffMinutes <= 0 && diffSeconds <= 0) {
            diff = "At Platform since " + diff
        }

        let departure = new Date(info.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime)
        let timeAtStation = departure - arrival
        timeAtStation = Math.floor(timeAtStation / 1000) + "s";
        if (timeAtStation == "0s" || timeAtStation == "NaNs") {
            timeAtStation = null
        }
        let misson = ""
        if (info.MonitoredVehicleJourney.JourneyNote.length == 0) {
            console.log("No mission")
            misson = ""
        }
        else {
            misson = info.MonitoredVehicleJourney.JourneyNote[0].value
        }
        if (info.MonitoredVehicleJourney.JourneyNote == undefined) {
            info.MonitoredVehicleJourney.JourneyNote[0] = { value: "" }
        }
        tempData = {
            line: lineData,
            direction: info.MonitoredVehicleJourney.DestinationName[0].value,
            mission: misson,
            atStop: info.MonitoredVehicleJourney.MonitoredCall.VehicleAtStop,
            arrivalAtStationEXP: info.MonitoredVehicleJourney.MonitoredCall.ExpectedArrivalTime,
            departureAtStationEXP: info.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime,
            arrivalAtStationAIM: info.MonitoredVehicleJourney.MonitoredCall.AimedArrivalTime,
            status: info.MonitoredVehicleJourney.MonitoredCall.ArrivalStatus,
            platform: info.MonitoredVehicleJourney.MonitoredCall.ArrivalPlatformName.value,
            trainLenght: info.MonitoredVehicleJourney.VehicleFeatureRef[0],
            arrivalIn: diff,
            arrivalTemp: arrivalTemp,
            timeAtStation: timeAtStation,
            isLive: isLive
        }
        returnData.push(tempData);
        console.log("Direction : ", tempData.direction)
        console.log("Mission : ", tempData.mission)
        console.log("Arrival in : ", tempData.arrivalIn)
        console.log("Platform : ", tempData.platform)
        console.log("Time at station : ", tempData.timeAtStation)
        console.log("Line : ", tempData.line.name)
        console.log("##################")
        console.groupEnd()

    }
    returnData.sort((a, b) => new Date(a.arrivalTemp) - new Date(b.arrivalTemp));
    return returnData;
}


// Function to update the hour element on the page
// Is called every second
// No return
function updateHour() {
    const date = new Date();
    const hours = date.getHours() < 10 ? `0${date.getHours()}` : date.getHours();
    const minutes = date.getMinutes() < 10 ? `0${date.getMinutes()}` : date.getMinutes();
    const seconds = date.getSeconds() < 10 ? `0${date.getSeconds()}` : date.getSeconds();
    const time = `${hours}:${minutes}:${seconds}`;

    document.getElementById('time').textContent = time;
}


//Main function to request a new station
//Is called when the page is loaded, when the user press enter in the input or when the user click on a suggestion
//Also called every minute without showing the loader
//No return
async function main(showLoader = true, filter = []) { //showLoader is a boolean to show or not the loader
    if (showLoader) {
        loading(true)
    }
    let querry = document.getElementById("city").value
    if (querry == "") { //If the input is empty, return
        if (showLoader) {
            loading(false)
        }
        return
    }
    let stationID = await getStations(querry, 1)
    document.getElementById("city").value = stationID[0].arrname
    stationID = stationID[0].zdaid
    let data = await getFutureTrainDepartures(stationID)
    let departures = await formatNextDepartures(data)
    document.querySelectorAll('body > div').forEach(div => { //Remove all the trainContainer divs
        if (!div.classList.contains('train-info') && !div.classList.contains('loaderDiv')) {
            div.remove();
        }
    });
    let listLine = [] //List of all the lines of the current result to show in the dropdown
    let listDestination = [] //List of all the destinations of the current result to show in the dropdown
    departures.forEach(element => {
        let color = "#ffffff" //Default color
        let displayState = "flex" //Default display 
        let platformTime = element.timeAtStation //Time at station
        if (!listLine.includes(element.line.name)) { //If the line is not already in the list, add it
            listLine.push(element.line.name)
        }
        if (!listDestination.includes(element.direction)) { //If the direction is not already in the list, add it
            listDestination.push(element.direction)
        }
        if (filter.length != 0) { //If there is a filter
            if (!filter[0].includes(element.direction) && filter[0].length != 0) { //If the direction is not in the filter and the filter is not empty,
                displayState = "none"
            }
            if (!filter[1].includes(element.line.name) && filter[1].length != 0) { //If the line is not in the filter and the filter is not empty,
                displayState = "none"
            }
        }
        if (element.isLive) { //If the data we get from the API is live(following the train), set the color to lightgreen
            color = "lightgreen"
        }
        if (platformTime == null) { //If the time at station could not be determined, set it to an empty string
            platformTime = "";
        }

        let div = document.createElement("div")
        div.classList.add("trainContainer")
        div.style.display = displayState

        div.innerHTML = `
        <div class="train-item">
            <div class="logo">
                <img src="${element.line.image.url}" alt="">
                <span>${element.mission}</span>
            </div>
            <div class = "destination">${element.direction}</div>
            <div class="time-station">${platformTime}</div>

            <div class = "time-info" style="color:${color}">${element.arrivalIn}</div>
        </div>
        <div class="platform">${element.platform}</div>
        <div style="display: none" class="data">${JSON.stringify(element)}</div>`

        document.body.appendChild(div);
    });
    let lineSelectEL = document.getElementById('lineMenu')
    let destinationSelectEL = document.getElementById('directionMenu')
    if (listLine.length <= 1) { //If there is only one line, hide the line dropdown
        console.log("Only one line")
        lineSelectEL.style.display = "none"
        document.getElementById('lineButton').style.display = "none"
    } else {
        document.getElementById('lineButton').style.display = "block"
    }
    if (listDestination.length <= 1) { //If there is only one destination, hide the destination dropdown
        destinationSelectEL.style.display = "none"
        document.getElementById('directionButton').style.display = "none"
    } else {
        document.getElementById('directionButton').style.display = "block"
    }
    listLine.forEach(line => { //Create the line dropdown
        let li = document.createElement('li')
        li.innerHTML = `<input type=checkbox value="${line}" id="${line}" class="checkboxLine" />${line}`
        li.addEventListener('click', function () {
            document.getElementById(line).checked = !document.getElementById(line).checked
            filterResults()
        })
        lineSelectEL.appendChild(li)
    })
    listDestination.forEach(destination => { //Create the destination dropdown
        let li = document.createElement('li')
        li.innerHTML = `<input type=checkbox value="${destination}" id="${destination}" class="checkboxDesti"/>${destination}`
        li.addEventListener('click', function () {
            document.getElementById(destination).checked = !document.getElementById(destination).checked
            filterResults()
        })
        destinationSelectEL.appendChild(li)
    })
    if (showLoader) {
        loading(false)
    }
}


//Function to loop through the trainContainer divs and update the time every second
//Is called every second
//No return
function loop() {
    document.querySelectorAll('body > div.trainContainer').forEach(div => {
        if (div.querySelector('.data') == null) {
            return;
        }
        const data = JSON.parse(div.querySelector('.data').textContent);
        const timeInfo = div.querySelector('.time-info');

        const arrivalTime = new Date(data.arrivalTemp); //2025-02-05T14:10:44.000Z
        let whenToRemove = new Date(arrivalTime).getTime();
        let timeAtPlatform = data.timeAtStation;
        if (timeAtPlatform != undefined) {
            timeAtPlatform = timeAtPlatform.slice(0, -1);
        }
        else {
            timeAtPlatform = 0;
        }

        const now = new Date();
        const diff = (arrivalTime - now);
        whenToRemove = new Date(whenToRemove + timeAtPlatform * 1000 + 5000);
        if (now > whenToRemove) {
            div.remove();
        } else {
            const diffMinutes = Math.floor(diff / 60000);
            const diffSeconds = Math.floor((diff % 60000) / 1000);

            const onlySecondsDiff = Math.floor(diff / 1000);
            timeInfo.textContent = `${diffMinutes}m ${diffSeconds}s`;
            if (diffMinutes <= 0 && diffSeconds <= 0) {
                timeInfo.textContent = "🚉 ➡️ " + -onlySecondsDiff + "s ";
            }
        }
    });
}


//Function to show or hide the loader
//Is called when the page is loaded, when the user press enter in the input or when the user click on a suggestion
//No return
function loading(isLoading) {
    if (isLoading) {
        loaderDiv.style.display = "flex";
    }
    else {
        loaderDiv.style.display = "none";
    }
}


//Function to create the search suggestions
//Is called when the user types in the input
//No return
async function createSearchSuggestions() {
    const input = document.getElementById("city");
    const suggestionsDiv = document.getElementById("suggestionContainer");
    input.addEventListener("input", async function () {
        const value = input.value;

        let stations = await getStations(value, 15);
        let uniqueStations = [];
        const seenZdaids = new Set();
        if (stations.length > 1) {
            for (const station of stations) {
                if (!seenZdaids.has(station.zdaid)) {
                    uniqueStations.push(station);
                    seenZdaids.add(station.zdaid);
                }
            }
        }
        stations = uniqueStations;
        suggestionsDiv.innerHTML = "";
        stations.forEach(station => {
            const div = document.createElement("div");
            div.classList.add("suggestion");
            div.textContent = station.arrname;
            div.addEventListener("click", function () {
                input.value = station.arrname;
                suggestionsDiv.innerHTML = "";
                main();
            });

            suggestionsDiv.appendChild(div);
        });
    });

}


//Function to get the user GPS coordinates
//Is called when the page is loaded
//No return
//If geolocation is supported, call getNearestStationFromGPS
async function getUserGPSCoordinates() {
    if (navigator.geolocation) {
        console.log("Requesting GPS coordinates")
        await navigator.geolocation.getCurrentPosition(async (position) => {
            position = [position.coords.longitude, position.coords.latitude]
            await getNearestStationFromGPS(position)
        });
    } else {
        console.error("Geolocation is not supported by this browser.");
    }
}


//Function to get the nearest station from GPS coordinates
//Return the nearest station
//Is called when the browser supports geolocation
//Call showPopUp
async function getNearestStationFromGPS(position) {
    loading(true)
    let latitude = position[1]
    let longitude = position[0]
    let data = await fetch("DataSet/arrets.json")
    data = await data.json()
    for (let station of data) {
        let stationLatitude = station.arrgeopoint.lat
        let stationLongitude = station.arrgeopoint.lon
        let distance = Math.sqrt(Math.pow(stationLatitude - latitude, 2) + Math.pow(stationLongitude - longitude, 2))
        station.distance = distance
    }
    data.sort((a, b) => a.distance - b.distance)
    console.log("Nearest station : ", data[0].arrname)
    loading(false)
    showPopUp(data[0])
    return data[0]
}


//Function to show a popup to ask the user if he wants to select the station
//No return
//Is called when the user is geolocated
async function showPopUp(station) {
    let stationName = station.arrname

    let div = document.createElement("div")
    div.classList.add("popup")
    div.innerHTML = `
    <div class="popup-content">
        <p>Do you want to select the station: ${stationName}?</p>
        <button id="yesButton">Yes</button>
        <button id="noButton">No</button>
    </div>
    `;
    let overlay = document.createElement("div")
    overlay.classList.add("overlay")
    document.body.appendChild(overlay);
    document.body.appendChild(div);


    document.getElementById("yesButton").addEventListener("click", function () {
        document.getElementById("city").value = stationName;
        console.log("Selected station : ", stationName)
        div.remove();
        overlay.remove();
        main();
    });

    document.getElementById("noButton").addEventListener("click", function () {
        console.log("User declined")
        div.remove();
        overlay.remove();
    });
}


//Function to filter the results
//No return
//Is called when the user select a line or a destination
function filterResults() {
    let allDestCheckbox = document.querySelectorAll('.checkboxDesti')
    let allLineCheckbox = document.querySelectorAll('.checkboxLine')

    let selectedDest = []
    let selectedLine = []

    allDestCheckbox.forEach(checkbox => {
        if (checkbox.checked) {
            selectedDest.push(checkbox.value)
        }
    })
    allLineCheckbox.forEach(checkbox => {
        if (checkbox.checked) {
            selectedLine.push(checkbox.value)
        }
    })


    // live update the results waiting for the refresh
    document.querySelectorAll('body > div.trainContainer').forEach(div => {
        if (div.querySelector('.data') == null) {
            return;
        }
        const data = JSON.parse(div.querySelector('.data').textContent);
        if (!selectedDest.includes(data.direction) && selectedDest.length != 0) {
            div.style.display = "none"
            console.log("Destination not in the list")
        }
        if (!selectedLine.includes(data.line.name) && selectedLine.length != 0) {
            div.style.display = "none"
            console.log("Line not in the list")
        }
        if ((selectedDest.includes(data.direction) || selectedDest.length == 0) && (selectedLine.includes(data.line.name) || selectedLine.length == 0)) {
            div.style.display = "flex"
        }
    });
    // main(false, [selectedDest, selectedLine])
}


//Function to setup the dropdowns
//No return
//Is called when the page is loaded
function setupDropdown(buttonId, menuId) {
    document
        .getElementById(buttonId)
        .addEventListener("click", function () {
            const menus = document.querySelectorAll(".dropdown-menu");
            menus.forEach(menu => {
                if (menu.id !== menuId) {
                    menu.classList.remove("active");
                }
            });
            document.getElementById(menuId).classList.toggle("active");
        });
    document.addEventListener("click", function (event) {
        if (!event.target.closest(".dropdown")) {
            document.getElementById(menuId).classList.remove("active");
        }
    });
}


//Function to get from the localstorage the last update seen
//Return the last update
//Is called on page loading and passed in parametters of showPopUpWithUpdate
function getLastUpdateSeen() {
    let data = localStorage.getItem("update")
    if (data == null) {
        return 0
    }
    return data
}


//Set the last update seen in the localstorage
//No return
//Is called after showPopUpWithUpate
function setLastUpdateSeen(update) {
    localStorage.setItem("update", update)
}


//Show a popup with the latest changes on the project
//No return
//Is called on pageloading
async function showPopUpWithUpdate(lastUpdateSaw) { //lastUpdateSaw is the id off the last seen update
    let updates = await fetch("DataSet/updates.json")
    updates = await updates.json()
    let unseenUpdates = updates.filter(update => update.id > lastUpdateSaw)
    if (unseenUpdates.length == 0) {
        getUserGPSCoordinates()
        return
    }
    let div = document.createElement("div")
    let txtToShow = ""
    unseenUpdates.forEach(update => {
        let addedTxt = ""
        if (update.added != undefined) {
            addedTxt = "<h4>🚀 - Added</h4><ul>"
            update.added.forEach(addedFeat => {
                addedTxt = addedTxt + `<li>${addedFeat}</li>`

            })
            addedTxt = addedTxt + "</ul>"
        }
        let fixedTxt = ""
        if (update.fixed != undefined) {
            fixedTxt = "<h4>🛠️ - Fixed</h4><ul>"
            update.fixed.forEach(fixedFeat => {
                fixedTxt = fixedTxt + `<li>${fixedFeat}</li>`
            })
            fixedTxt = fixedTxt + "</ul>"
        }

        let emoji = getRandomEmoji()

        txtToShow = txtToShow + `<h3>${emoji} - ${update.title}</h3> ${addedTxt} ${fixedTxt}`
    })

    div.classList.add("popup")
    div.innerHTML = `
            <div class="popup-content" style="max-height: 80vh; overflow-y: auto;">
                <p>Check out the new updates!</p>
                ${txtToShow}
            </div>`
    let overlay = document.createElement("div")
    overlay.classList.add("overlay")
    overlay.addEventListener("click", function () {
        div.remove();
        overlay.remove();
        getUserGPSCoordinates()
    })
    document.body.appendChild(overlay);
    document.body.appendChild(div);
    setLastUpdateSeen(unseenUpdates[unseenUpdates.length - 1].id)


}


//Get a random emoji
//Return an emoji
//Is called inside showPopUpWithUpdate
function getRandomEmoji() {
    const emojiRanges = [
        [0x1F600, 0x1F64F], // Emoticônes
        [0x1F300, 0x1F5FF], // Symboles divers
        [0x1F680, 0x1F6FF], // Transport & cartes
        [0x1F700, 0x1F77F], // Alchimie
        [0x1F780, 0x1F7FF], // Géométrie supplémentaire
        [0x1F800, 0x1F8FF], // Flèches supplémentaires
        [0x1F900, 0x1F9FF], // Supplémentaux
        [0x1FA00, 0x1FA6F], // Objets divers
    ];

    const range = emojiRanges[Math.floor(Math.random() * emojiRanges.length)];
    const emojiCode = Math.floor(Math.random() * (range[1] - range[0] + 1)) + range[0];
    return String.fromCodePoint(emojiCode);
}




document.getElementById("city").addEventListener("blur", function () { setTimeout(() => { document.getElementById("suggestionContainer").innerHTML = ""; }, 1000); });
document.getElementById("city").addEventListener("keypress", createSearchSuggestions())
document.getElementById("city").addEventListener("keypress", function (e) { if (e.key === 'Enter') { main() } })

setInterval(loop, 500);
setInterval(main(false), 30000);
setInterval(updateHour, 500);

setupDropdown("lineButton", "lineMenu");
setupDropdown("directionButton", "directionMenu");
showPopUpWithUpdate(getLastUpdateSeen())

main()