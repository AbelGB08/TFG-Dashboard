var socket = io.connect('http://' + document.domain + ':' + location.port);
var chart = null;
var ctx = null;
var charts = [];
var lastDate = null;
const maxDataPoints = 25;

function initCharts() {
    for (var i = 1; i <= 5; i++) {
        ctx = document.getElementById('ina' + i).getContext('2d');
        chart = new Chart(ctx, {
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
                animation: false,
                interaction: {
                    intersect: false,
                    mode: 'x'
                },
            }
        });
        charts.push(chart);
    }
    ctx = document.getElementById('temps').getContext('2d');
    chart = new Chart(ctx, {
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
            animation: false,
            interaction: {
                intersect: false,
                mode: 'x'
            },
        }
    });
    charts.push(chart);

    ctx = document.getElementById('sbc').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                    label: 'Amps1',
                    borderColor: "rgb(255,0,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    data: [],
                },
                {
                    label: 'Amps2',
                    borderColor: "rgb(255,255,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    data: [],
                },
                {
                    label: "Amps3",
                    borderColor: "rgb(0,0,255)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    lineTension: 0.5
                },
                {
                    label: "Amps4",
                    borderColor: "rgb(0,255,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    lineTension: 0.5
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            interaction: {
                intersect: false,
                mode: 'x'
            },
        }
    });
    charts.push(chart);

    ctx = document.getElementById('sbt').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                    label: 'temp1',
                    borderColor: "rgb(255,0,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    data: [],
                },
                {
                    label: 'temp2',
                    borderColor: "rgb(255,255,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    data: [],
                },
                {
                    label: "temp3",
                    borderColor: "rgb(0,0,255)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    lineTension: 0.5
                },
                {
                    label: "temp4",
                    borderColor: "rgb(0,255,0)",
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    lineTension: 0.5
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            interaction: {
                intersect: false,
                mode: 'x'
            },
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
        case 'temps':
            chart = charts[5];
            break;
        case 'sbc':
            chart = charts[6];
            break;
        case 'sbt':
            chart = charts[7];
            break;
    }
    if (chart.id != 5 && chart.id != 6 && chart.id != 7) {
        chart.data.labels.push(data.date.split(" ")[1]);
        chart.data.datasets[0].data.push(data.volts);
        chart.data.datasets[1].data.push(data.amps);
        chart.data.datasets[2].data.push(data.pow);
    } else {
        if (data.sensor == 'temps' || data.sensor == "sbt" || data.sensor == "sbc") {
            chart.data.labels.push(data.date.split(" ")[1]);
            chart.data.datasets[0].data.push(data.base);
            chart.data.datasets[1].data.push(data.chimenea);
            chart.data.datasets[2].data.push(data.exterior);
            chart.data.datasets[3].data.push(data.bandeja);
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