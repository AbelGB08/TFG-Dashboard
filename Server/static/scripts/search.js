ctx = document.getElementById('searchChart').getContext('2d');
chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
                label: 'A',
                borderColor: "rgb(255,0,0)",
                pointRadius: 5,
                pointHoverRadius: 10,
                data: [],
            },
            {
                label: 'B',
                borderColor: "rgb(255,255,0)",
                pointRadius: 5,
                pointHoverRadius: 10,
                data: [],
            },
            {
                label: "C",
                borderColor: "rgb(0,0,255)",
                pointRadius: 5,
                pointHoverRadius: 10,
                lineTension: 0.5
            },
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

document.getElementById('submitButton').addEventListener('click', async function () {
    const form = document.getElementById('dataForm');
    const formData = new FormData(form);
    const queryString = new URLSearchParams(formData).toString();

    var sensorName = queryString.split('&')[0].split('=')[1];

    try {
        const response = await fetch(`/getData?${queryString}`, {
            method: 'GET',
        });

        if (!response.ok) {
            throw new Error(`Error en la solicitud: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(data);
        var datasets = [], labels = [];
        for (var i = 0; i < data.data.length - 1; i++) {
            datasets[i] = {
                pointRadius: 5,
                pointHoverRadius: 10,
                data: data.data[i],
            };
        }
        if (sensorName === 'BT') {
            datasets[0].label = 'Base';
            datasets[0].borderColor = "rgb(255,0,0)";
            datasets[1].label = 'Chimenea';
            datasets[1].borderColor = "rgb(255,255,0)";
            datasets[2].label = 'Exterior';
            datasets[2].borderColor = "rgb(0,0,255)";
            datasets[3].label = 'Bandeja';
            datasets[3].borderColor = "rgb(0,255,0)";
        } else if (sensorName === 'SBC') {
            datasets[0].label = 'Amps1';
            datasets[0].borderColor = "rgb(255,0,0)";
            datasets[1].label = 'Amps2';
            datasets[1].borderColor = "rgb(255,255,0)";
            datasets[2].label = 'Amps3';
            datasets[2].borderColor = "rgb(0,0,255)";
            datasets[3].label = 'Amps4';
            datasets[3].borderColor = "rgb(0,255,0)";
        } else if (sensorName === 'SBT') {
            datasets[0].label = 'Temp1';
            datasets[0].borderColor = "rgb(255,0,0)";
            datasets[1].label = 'Temp2';
            datasets[1].borderColor = "rgb(255,255,0)";
            datasets[2].label = 'Temp3';
            datasets[2].borderColor = "rgb(0,0,255)";
            datasets[3].label = 'Temp4';
            datasets[3].borderColor = "rgb(0,255,0)";
        } else {
            datasets[0].label = 'Volts';
            datasets[0].borderColor = "rgb(255,0,0)";
            datasets[1].label = 'Amps';
            datasets[1].borderColor = "rgb(255,255,0)";
            datasets[2].label = 'Pow';
            datasets[2].borderColor = "rgb(0,0,255)";
        }
        labels = data.data[data.data.length - 1];

        if (chart) {
            chart.destroy();
        }
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
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
    } 
    catch (error) {
        console.error('Error:', error);
    }
});