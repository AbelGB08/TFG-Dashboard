import mysql from 'mysql'; // Import mysql
let lecturas;
//Create connection
const conector = mysql.createConnection(
    {
        host: 'localhost',
        user: 'abel',
        password: '12345',
        database: 'ina226'
    }
);

const conectar = () => {
    conector.connect(err => {
        console.log('Conectado a la base de datos.');
    })
}

const agregarLectura = (volts, amps, pow) => {
    const sql = `INSERT INTO lecturas (volts, amps, pow) VALUES (${volts}, ${amps}, ${pow})`;
    conector.query(sql, function(err, result, field){
        if (err) throw err;
        console.log(result);
    });
}

const obtenerLecturas = () => {
    const sql = 'SELECT * FROM lecturas';
    conector.query(sql, function(err, result, field){
        lecturas = result;
    });
    console.log(lecturas);
    return lecturas;
}

export { agregarLectura, obtenerLecturas };