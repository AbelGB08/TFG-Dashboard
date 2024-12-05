var socket = io.connect('http://' + document.domain + ':' + location.port);
const maxDataPoints = 25;
let charts = [];

// Configuración base de las gráficas
const baseChartOptions = {
    type: 'line',
    options: {
        responsive: true,
        animation: false,
        interaction: {
            intersect: false,
            mode: 'x'
        }
    }
};

// Configuración de datasets para las diferentes gráficas
const chartConfigurations = {
    INA: {
        labels: ['Volts', 'Amps', 'Pow'],
        colors: ['rgb(255,0,0)', 'rgb(255,255,0)', 'rgb(0,0,255)']
    },
    temps: {
        labels: ['Base', 'Chimenea', 'Exterior', 'Bandeja'],
        colors: ['rgb(255,0,0)', 'rgb(255,255,0)', 'rgb(0,0,255)', 'rgb(0,255,0)']
    },
    sbc: {
        labels: ['Amps1', 'Amps2', 'Amps3', 'Amps4'],
        colors: ['rgb(255,0,0)', 'rgb(255,255,0)', 'rgb(0,0,255)', 'rgb(0,255,0)']
    },
    sbt: {
        labels: ['Temp1', 'Temp2', 'Temp3', 'Temp4'],
        colors: ['rgb(255,0,0)', 'rgb(255,255,0)', 'rgb(0,0,255)', 'rgb(0,255,0)']
    }
};

function createDatasets(labels, colors) {
    return labels.map(function(label, index) {
        return {
            label: label,
            borderColor: colors[index],
            pointRadius: 5,
            pointHoverRadius: 10,
            lineTension: 0.5,
            data: []
        };
    });
}

function createChart(ctx, configKey) {
    const config = chartConfigurations[configKey];
    return new Chart(ctx, {
        ...baseChartOptions,
        data: {
            labels: [],
            datasets: createDatasets(config.labels, config.colors)
        }
    });
}

function initCharts() {
    for (let i = 1; i <= 5; i++) {
        const ctx = document.getElementById('ina' + i).getContext('2d');
        charts.push(createChart(ctx, 'INA'));
    }

    ['temps', 'sbc', 'sbt'].forEach(function(id) {
        const ctx = document.getElementById(id).getContext('2d');
        charts.push(createChart(ctx, id));
    });
}

initCharts();

// Actualizar las gráficas
socket.on('update_chart', function (data) {
    const chartIndex = {
        'INA1': 0, 'INA2': 1, 'INA3': 2, 'INA4': 3, 'INA5': 4,
        'temps': 5, 'sbc': 6, 'sbt': 7
    }[data.sensor];

    if (chartIndex === undefined) return; // No hacer nada si el sensor es incorrecto

    const chart = charts[chartIndex];
    chart.data.labels.push(data.date.split(" ")[1]); // Usar solo la hora en lugar de la fecha completa

    // Obtener las keys de los datos a actualizar
    const updateKeys = Object.keys(data).filter(function(key) {
        return key !== 'sensor' && key !== 'date';
    });

    // Actualizar los datasets
    updateKeys.forEach(function(key, idx) {
        chart.data.datasets[idx].data.push(data[key]);
    });

    // Limitar datos a maxDataPoints
    if (chart.data.labels.length > maxDataPoints) {
        chart.data.labels.shift(); // Eliminar la fecha más antigua
        chart.data.datasets.forEach(function(dataset) {
            dataset.data.shift(); // Eliminar los datos más antiguos
        });
    }

    chart.update();
});