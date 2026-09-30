import { createClient } from 'redis';
import { REDIS_URL, REDIS_PASSWORD } from '../config/utils.js';

let redis = null;

export async function connectToRedis() {
  if (!REDIS_URL) {
    console.log('Redis not configured, cache disabled.');
    return;
  }
  redis = createClient({
    url: REDIS_URL,
    password: REDIS_PASSWORD,
    disableOfflineQueue: true,
    socket: { connectTimeout: 5000 },
  });
  redis.on('error', () => console.error('Redis connection error'));
  await redis.connect();
  console.log('Redis connected');
}

export function getRedisClient() { return redis; }
