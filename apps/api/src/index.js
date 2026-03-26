require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 3001;

// Middlewares
app.use(cors());
app.use(express.json());

// Conexión a Base de Datos (Postgres)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Ruta de prueba
app.get('/', (req, res) => {
  res.json({ message: 'API La Casita funcionando ' });
});

// Ruta de ejemplo: Obtener productos
app.get('/api/inventory', async (req, res) => {
  try {
    // Consulta de prueba para ver si conecta la DB
    const result = await pool.query('SELECT NOW()');
    res.json({ 
      status: 'Conectado a la base de datos',
      time: result.rows[0]
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Error en el servidor');
  }
});

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});