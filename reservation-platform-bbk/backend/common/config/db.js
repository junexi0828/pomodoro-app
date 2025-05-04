// db.js
const mysql = require('mysql2');
require('dotenv').config();

const pool = mysql.createPool({
host: process.env.DB_HOST,
user: process.env.DB_USER,
password: process.env.DB_PASS,
database: process.env.DB_NAME,
waitForConnections: true,
connectionLimit: 10,
queueLimit: 0
});

module.exports = pool.promise();

console.log('DB:', process.env.DB_HOST, process.env.DB_USER, process.env.DB_PASS, process.env.DB_NAME);