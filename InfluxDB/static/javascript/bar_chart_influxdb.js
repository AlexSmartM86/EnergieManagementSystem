        // Daten von Flask abrufen
        fetch('/data')
            .then(response => response.json())
            .then(data => {
                // Extrahiere Timestamps und Werte aus den empfangenen Daten
                const timestamps = data[0];
                const values_pv = data[1];
                const values_fromgrid = data[2];
                const values_togrid = data[3];
                console.log(timestamps);

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
            })
            .catch(error => console.error('Error fetching data:', error));