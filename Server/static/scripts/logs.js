var socket = io.connect(`http://${document.domain}:${location.port}`);

const logFeed = document.getElementById('log-feed');
const sensorInput = document.getElementById('sensorName');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const submitButton = document.getElementById('submitButton');

socket.on('log', function(log) {
    try {
        const newLog = document.createElement('div');
        newLog.className = 'log';
        const newLogDate = document.createElement('div');
        newLogDate.className = 'log-date';
        const newLogMessage = document.createElement('div');
        newLogMessage.className = 'log-message';

        newLogDate.textContent = log.date;
        newLogMessage.textContent = log.message;
        
        newLog.appendChild(newLogDate);
        newLog.appendChild(newLogMessage);
        logFeed.appendChild(newLog);

        logFeed.scrollTop = logFeed.scrollHeight;

        newLog.addEventListener('click', function() {
            sensorInput.value = log.sensor;
            startDateInput.value = formatToDatetimeLocalWithOffset(newLogDate.textContent, -1);
            endDateInput.value = formatToDatetimeLocalWithOffset(newLogDate.textContent, 1);
            submitButton.click();
        });
    } catch (error) {
        console.error('Error processing log:', error);
    }
});

function formatToDatetimeLocalWithOffset(dateString, offsetMinutes) {
    // Dividir la fecha y la hora
    const [datePart, timePart] = dateString.split(' ');

    // Separar los componentes de la fecha
    const [day, month, year] = datePart.split('-');

    // Separar los componentes de la hora
    const [hours, minutes, seconds] = timePart.split(':');

    // Crear un objeto Date en UTC
    const date = new Date(Date.UTC(year, month - 1, day, hours, minutes, seconds));

    // Agregar el offset
    date.setMinutes(date.getMinutes() + offsetMinutes);

    // Formatear la fecha a "YYYY-MM-DDTHH:mm"
    const formattedDate = date.toISOString().slice(0, 16);
    
    return formattedDate;
}