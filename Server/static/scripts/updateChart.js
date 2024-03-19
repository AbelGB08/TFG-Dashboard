var socket = io.connect('http://' + document.domain + ':' + location.port);
var charts = [];
var lastDate = null;
const maxDataPoints = 50;

function initCharts() {
    for (var i = 1; i <= 5; i++) {
        var ctx = document.getElementById('ina' + i).getContext('2d');
        var chart = new Chart(ctx, {
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
                    }
                ]
            },
            options: {
                responsive: true,
                animation: false
            }
        });
        charts.push(chart);
    }
    var ctx = document.getElementById('temps').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                    label: 'Base',
                    borderColor: "rgb(255,0,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    data: [],
                },
                {
                    label: 'Chimenea',
                    borderColor: "rgb(255,255,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    data: [],
                },
                {
                    label: "Exterior",
                    borderColor: "rgb(0,0,255)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    lineTension: 0.5
                },
                {
                    label: "Bandeja",
                    borderColor: "rgb(0,255,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    lineTension: 0.5
                }
            ]
        },
        options: {
            responsive: true,
            animation: false
        }
    });
    charts.push(chart);
}

initCharts();

socket.on('update_chart', function(data) {
    var chart = null;

    switch (data.sensor) {
        case 'INA1':
            chart = charts[0];
            break;
        case 'INA2':
            chart = charts[1];
            break;
        case 'INA3':
            chart = charts[2];
            break;
        case 'INA4':
            chart = charts[3];
            break;
        case 'INA5':
            chart = charts[4];
            break;
        default:
            chart = charts[5];
    }
    if (chart.id != 5) {
        chart.data.labels.push(data.date.split(" ")[1]);
        chart.data.datasets[0].data.push(data.volts);
        chart.data.datasets[1].data.push(data.amps);
        chart.data.datasets[2].data.push(data.pow);
    } else {
        if (data.date.split(" ")[1] !== lastDate) { // Comprueba si el date es diferente al último date agregado
            chart.data.labels.push(data.date.split(" ")[1]);
            lastDate = data.date.split(" ")[1]; // Actualiza el último date agregado
        }
        switch (data.sensor) {
            case 'temp1':
                chart.data.datasets[0].data.push(data.temp);
                break;
            case 'temp2':
                chart.data.datasets[1].data.push(data.temp);
                break;
            case 'temp3':
                chart.data.datasets[2].data.push(data.temp);
                break;
            case 'temp4':
                chart.data.datasets[3].data.push(data.temp);
                break;

        }
    }

    if (chart.data.labels.length > maxDataPoints) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(dataset => {
            dataset.data.shift();
        });
    }

    chart.update();
});