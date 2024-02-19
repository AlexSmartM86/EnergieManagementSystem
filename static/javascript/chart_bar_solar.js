// Funktion zum Erstellen des Diagramms
var createBarChart = (canvasId, xData, yData) => {
    var canvas = document.getElementById(canvasId);
    var context = canvas.getContext('2d');

    // Erstelle den Chart auf dem neuen Canvas-Element
    var context = canvas.getContext('2d');
    var data = {
        labels: xData,
        datasets: [{
            label: 'Solarprognose',
            data: yData,
            backgroundColor: 'rgba(252, 144, 3, 1)',
            borderColor: 'rgba(252, 144, 3, 1)',
        }]
    };
    var config = {
        type: 'bar',
        data: data
    };
    var chart = new Chart(context, config);

    // Optional: Speichere das Chart-Objekt für spätere Verwendung oder Zerstöre es bei Bedarf
    // window.myChart = chart;
    // window.myChart.destroy();
};

// Rufe die Daten ab und erstelle das Diagramm
axios.get('https://api.forecast.solar/estimate/watt_hours_period/52/7/15/0/30')
.then((response) => {
    var data = response.data.result;
    var xData = [];
    var yData = [];
    for (var property in data) {
        var datum = new Date(property);
        var hours = datum.getHours();
        var minutes = "0" + datum.getMinutes();
        var time = hours + ":" + minutes.substr(-2); // Formatierung der Zeit
        xData.push(time);
        yData.push(data[property]);
    }
    createBarChart("solar-chart", xData, yData);
});