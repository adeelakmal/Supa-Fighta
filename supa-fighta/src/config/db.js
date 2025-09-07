const config = require('./dotenv')
const { Pool } = require("pg");

const pool = new Pool({
   connectionString: config.pg_url
});

pool.connect()
.then(client => {
   console.log("✅ Database connected successfully");
   client.release()
})
.catch(err => {
   console.error("Database connection error:", err);
   process.exit(1);
})


module.exports = pool;