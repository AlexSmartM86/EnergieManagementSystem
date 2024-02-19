var myChartObject = document.getElementById('mychart');

var chart = new Chart(myChartObject, {
    type: 'bar',
    data: {
        labels: ["Januar", "Februar", "März", "April"],
        datasets: [{
            label: "Datensatz Nummer 1",
            data: [25, 19, 21, 35],
            backgroundColor: 'rgba(255, 51, 204, 0.5)',
            borderColor: 'rgba(255, 51, 204, 1)'
        }],
    },
    optios: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    },
});