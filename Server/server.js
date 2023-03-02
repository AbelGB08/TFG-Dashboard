const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());

// Database connection params
const connection = mysql.createConnection({
    host: 'localhost',
    user: 'abel',
    password: '12345',
    database: 'ina226'
});

// Connect to database
connection.connect(error => {
    if (error) throw error;
    console.log('Conectado a la base de datos');
});

// Start listening
app.listen(PORT, () => {
    console.log(`Servidor escuchando en el puerto ${PORT}`);
});

// Routes
app.get('/', (req, res) => {
    console.log('Nueva conexión: ', req.ip.substr(7));
    res.send('HOLA QUE PACHA COÑO');
});

// Retrieve data from startDate to endDate
app.get('/getData/:startDate/:endDate', (req, res) => { 
    var magnitude, startDate, endDate, sql;
    startDate = req.params.startDate;
    endDate = req.params.endDate;
    sql = `SELECT volts, amps, pow, date FROM lecturas WHERE date BETWEEN '${startDate}' AND '${endDate}'`;
    connection.query(sql, (error, results) => {
        if (error) throw error;
        if (results.length > 0) {
            res.json(results);
        } else {
            res.send('SIN RESULTADOS');
        }
    });

})