import dotenv from 'dotenv';
import { readFileSync } from 'node:fs';
dotenv.config();

function secret(name) {
  const file = process.env[`${name}_FILE`];
  return file ? readFileSync(file, 'utf8').trim() : process.env[name];
}

const PORT = process.env.PORT;
const database = process.env.MONGO_DATABASE || 'wanderlust';
const password = secret('MONGO_PASSWORD');
const MONGODB_URI = process.env.MONGODB_URI || (password
  ? `mongodb://${encodeURIComponent(process.env.MONGO_USER || 'wanderlust')}:${encodeURIComponent(password)}@${process.env.MONGO_HOST || 'mongodb'}:27017/${database}?authSource=${database}`
  : undefined);
const REDIS_URL = process.env.REDIS_URL;
const REDIS_PASSWORD = secret('REDIS_PASSWORD');
const JWT_SECRET = secret('JWT_SECRET');

export { MONGODB_URI, PORT, REDIS_URL, REDIS_PASSWORD, JWT_SECRET };
