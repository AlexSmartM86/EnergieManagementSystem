
var ctx = document.getElementById('myChart').getContext('2d');
var myChart;

$(document).ready(function() {
    // Dein jQuery-Code hier...
});

// Funktion zum Aktualisieren des Charts
function updateChart(response) {
    const timestamps = response[0];
    const values_pv = response[1];
    const values_fromgrid = response[2];
    const values_togrid = response[3];

    // Erstelle ein Chart mit Chart.js
    var ctx = document.getElementById('myChart').getContext('2d');
    if (myChart) myChart.destroy(); // Aktuelles Chart zerstören
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: timestamps,
            datasets: [
                {
                  label: 'PV-Leistung',
                  data: values_pv,
                  pointStyle: false,
                  backgroundColor: 'rgb(250, 153, 7)',
                },
                {
                  label: 'Bezug',
                  data: values_fromgrid,
                  pointStyle: false,
                  backgroundColor: 'rgb(250, 7, 100)',
                },
                {
                  label: 'Einspeisung',
                  data: values_togrid,
                  pointStyle: false,
                  backgroundColor: 'rgb(7, 250, 117)',                  
                },
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Energieverteilung'
                },
            },
            responsive: true,
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        autoSkip: true,
                        maxRotation: 0,
                    },
                },
                y: {
                    stacked: true
                }
            }
        }
    });
}

// Formular absenden und Daten abrufen from Flask
$('#dateForm').submit(function(event) {
    event.preventDefault(); // Das Standardverhalten des Formulars verhindern
    var formData = $(this).serialize(); // Formulardaten serialisieren
    // AJAX-Anfrage an den Flask-Server senden
    $.ajax({
        type: 'POST',
        url: '/update_chart',
        data: formData,
        success: function(response) {
            updateChart(response); // Chart aktualisieren
        }
    });
});