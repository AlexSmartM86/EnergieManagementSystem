        // Daten von Flask abrufen
        fetch('/data')
            .then(response => response.json())
            .then(data => {
                // Extrahiere Timestamps und Werte aus den empfangenen Daten
                const timestamps = data.timestamps;
                const values = data.values;

                // Erstelle ein Chart mit Chart.js
                var ctx = document.getElementById('myChart').getContext('2d');
                var myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: timestamps,
                        datasets: [{
                            label: 'Stromleistung',
                            data: values,
                            pointStyle: false,
                            fill: true,
                            fillColor: 'rgb(245, 5, 217)',
                            borderColor: 'rgb(245, 5, 217)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            })
            .catch(error => console.error('Error fetching data:', error));