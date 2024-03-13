var socket = io.connect('http://' + document.domain + ':' + location.port);
var ctx1 = document.getElementById('ina1').getContext('2d');
var ctx2 = document.getElementById('ina2').getContext('2d');
const maxDataPoints = 10;

var ina1 = new Chart(ctx1, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Volts',
            borderColor: "rgb(255,0,0)",
            pointRadius: 5,
            pointHoverRadius: 10,
            data: [],
        }, 
        {
            label: 'Amps',
            borderColor: "rgb(255,255,0)",
            pointRadius: 5,
            pointHoverRadius: 10,
            data: [],
        },
        {
            label: "Pow",
            borderColor: "rgb(0,0,255)",
            pointRadius: 5,
            pointHoverRadius: 10,
            lineTension: 0.5
        }]
    },
    options: {
        responsive: true,
        animation: false
    }
});

var ina2 = new Chart(ctx2, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Volts',
            borderColor: "rgb(255,0,0)",
            pointRadius: 5,
            pointHoverRadius: 10,
            data: [],
        }, 
        {
            label: 'Amps',
            borderColor: "rgb(255,255,0)",
            pointRadius: 5,
            pointHoverRadius: 10,
            data: [],
        },
        {
            label: "Pow",
            borderColor: "rgb(0,0,255)",
            pointRadius: 5,
            pointHoverRadius: 10,
            lineTension: 0.5
        }]
    },
    options: {
        responsive: true,
        animation: false
    }
});

socket.on('update_chart', function(data) {
    var chart = null;
    switch (data.sensor) {
        case 'INA1':
            chart = ina1;
            break;
        case 'INA2':
            chart = ina2;
            break;
        case 'INA3':
            chart = ina3;
            break;
        case 'INA4':
            chart = ina4;
            break;
        case 'INA5':
            chart = ina5;
            break;
    }
    chart.data.labels.push(data.date);
    chart.data.datasets[0].data.push(data.volts);
    chart.data.datasets[1].data.push(data.amps);
    chart.data.datasets[2].data.push(data.pow);

    if (chart.data.labels.length > maxDataPoints) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(dataset => {
            dataset.data.shift();
        });
    }

    chart.update();
});