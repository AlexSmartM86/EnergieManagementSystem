
var canv = window.document.getElementById("chart-awattar")
var context = canv.getContext('2d');



//Funktionen
var createBarChart1 = (xData, yData) => {
    var data = {
        labels: xData,
        datasets: [{
            label: 'Strompreise',
            data: yData,
            backgroundColor: 'rgba(255, 3, 200, 1)',
            borderColor: 'rgba(255, 3, 200, 1)',
        }]
    }
    var config = {
        type: 'bar',
        data: data
    }
    var chart1 = new Chart(context, config);
}


// Rufe die Daten ab
axios.get('https://api.awattar.de/v1/marketdata')
.then((response)=>{
    var data = response.data.data;
    var xData = [];
    var yData = [];
    for(var i = 0; i < data.length; i++){
        var timestamp = (data[i].start_timestamp);
        var timeuni = new Date(timestamp);
        var hours = timeuni.getHours();
        var minutes = "0" + timeuni.getMinutes();
        var time = (hours + ":" + minutes);
        xData.push(time);
        yData.push(data[i].marketprice);
    }
    createBarChart1(xData, yData);
});
