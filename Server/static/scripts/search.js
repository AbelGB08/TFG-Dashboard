ctx = document.getElementById('searchChart').getContext('2d');
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

    try {
        const response = await fetch(`/getData?${queryString}`, {
            method: 'GET',
        });

        if (!response.ok) {
            throw new Error(`Error en la solicitud: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(data);
        
        chart.data.datasets[0].data = data.data[0];
        chart.data.datasets[1].data = data.data[1];
        chart.data.datasets[2].data = data.data[2];
        chart.data.labels = data.data[3];
        chart.update();
    } 
    catch (error) {
        console.error('Error:', error);
    }
});