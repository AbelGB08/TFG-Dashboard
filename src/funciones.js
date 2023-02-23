const volts = document.querySelector('#volts');
const amps = document.querySelector('#amps');
const pow = document.querySelector('#pow');
const btnAgregar = document.querySelector('#btn_agregar');

btnAgregar.addEventListener('click', function(){
    window.location.href = `agregar/${volts.value}/${amps.value}/${pow.value}`;
});