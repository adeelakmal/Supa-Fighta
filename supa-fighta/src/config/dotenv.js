const dotenv = require('dotenv');

dotenv.config();

const username = encodeURIComponent(process.env.PG_USERNAME || '');
const password = encodeURIComponent(process.env.PG_PASSWORD || '');
const database = encodeURIComponent(process.env.PG_DATABASE || '');
const fallbackPgUrl = `postgresql://${username}:${password}@${process.env.PG_HOST}/${database}?sslmode=require`;

module.exports = {
    port: Number(process.env.PORT) || 8080,
    pg_url: process.env.DATABASE_URL || fallbackPgUrl
};
