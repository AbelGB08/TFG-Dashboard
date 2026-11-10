var socket = io.connect('http://' + document.domain + ':' + location.port);
// Escucha el evento 'actualizar_temperatura'
socket.on('update_temp', function(data) {
    var tempItem = document.getElementById(data.id);
    tempItem.textContent = data.temp + ' °C';
});