
function fetchData_pv() {
    fetch('/pv-leistung')
        .then(response => response.json())
        .then(data => {
            const wert = data.values;
            var strom = document.getElementById('pv');
            strom.innerHTML = `PV-Leistung: ${data} Watt`;
        });
}
// Daten alle 10 Sekunden abrufen
setInterval(fetchData_pv, 10000);



function fetchData_fromg() {
    fetch('/bezug')
        .then(response => response.json())
        .then(data => {
            const wert = data.values;
            var strom = document.getElementById('bezug');
            strom.innerHTML = `Bezug: ${data} Watt`;
        });
}
// Daten alle 10 Sekunden abrufen
setInterval(fetchData_fromg, 10000);



function fetchData_togr() {
    fetch('/einspeisung')
        .then(response => response.json())
        .then(data => {
            const wert = data.values;
            var strom = document.getElementById('einspeisung');
            strom.innerHTML = `Einspeisung: ${data} Watt`;
        });
}
// Daten alle 10 Sekunden abrufen
setInterval(fetchData_togr, 10000);
