import express from 'express' // Import express
import { agregarLectura, obtenerLecturas } from './src/mysqlConnector.js';

let lecturas;
const app = express(); // Init express

// Init server
app.listen('8000', function() {
    console.log('Aplicacion iniciada en el puerto 8000');
});

// Pug config
app.set('views', './vistas');
app.set('view engine', 'pug');

// Static files config
app.use(express.static('./vistas'));
app.use(express.static('./src'));
app.use(express.static('./css'));

app.get('/', function(req, res) {
    lecturas = obtenerLecturas();
    res.render('index', {titulo: 'TFG Dashboard INA226', lecturas: lecturas});
});

app.get('/agregar/:volts/:amps/:pow', function(req, res){
    let volts = req.params.volts;
    let amps = req.params.amps;
    let pow = req.params.pow;
    agregarLectura(volts, amps, pow);
    res.redirect('/');

    console.log(volts, amps, pow);
})
