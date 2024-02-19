
function fetchData() {
    fetch('/leistung')
        .then(response => response.json())
        .then(data => {
            const wert = data.values;
            var strom = document.getElementById('wert');
            strom.innerHTML = `Aktuelle Leistung: ${data} Watt`;
        });
}
// Daten alle 10 Sekunden abrufen
setInterval(fetchData, 10000);



function fetchData() {
    fetch('/pv-leistung')
        .then(response => response.json())
        .then(data => {
            const wert = data.values;
            var strom = document.getElementById('pv');
            strom.innerHTML = `Aktuelle PV-Leistung: ${data} Watt`;
        });
}
// Daten alle 10 Sekunden abrufen
setInterval(fetchData, 10000);



function fetchData() {
    fetch('/bezug')
        .then(response => response.json())
        .then(data => {
            const wert = data.values;
            var strom = document.getElementById('bezug');
            strom.innerHTML = `Aktueller Bezug: ${data} Watt`;
        });
}
// Daten alle 10 Sekunden abrufen
setInterval(fetchData, 10000);



function fetchData() {
    fetch('/einspeisung')
        .then(response => response.json())
        .then(data => {
            const wert = data.values;
            var strom = document.getElementById('einspeisung');
            strom.innerHTML = `Aktuelle Einspeisung: ${data} Watt`;
        });
}
// Daten alle 10 Sekunden abrufen
setInterval(fetchData, 10000);
