const config = require('./dotenv')
const { Pool } = require("pg");

const pool = new Pool({
   connectionString: config.pg_url
});

module.exports = pool;