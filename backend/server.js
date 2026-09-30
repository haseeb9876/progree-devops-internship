import compression from 'compression';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import express from 'express';
import mongoose from 'mongoose';
import connectDB from './config/db.js';
import { PORT, REDIS_URL } from './config/utils.js';
import authRouter from './routes/auth.js';
import postsRouter from './routes/posts.js';
import { connectToRedis, getRedisClient } from './services/redis.js';
const app = express();
const port = PORT || 5000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());
app.use(cookieParser());
app.use(compression());
app.get('/health/live', (req, res) => res.json({ status: 'ok' }));
app.get('/health/ready', (req, res) => {
  const mongodb = mongoose.connection.readyState === 1;
  const redis = !REDIS_URL || Boolean(getRedisClient()?.isReady);
  res.status(mongodb && redis ? 200 : 503).json({
    status: mongodb && redis ? 'ready' : 'unavailable', mongodb, redis,
  });
});
app.use('/api/posts', postsRouter);
app.use('/api/auth', authRouter);
app.get('/', (req, res) => res.send('Yay!! Backend of wanderlust app is now accessible'));

async function start() {
  await connectDB();
  await connectToRedis();
  const server = app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on port ${port}`);
  });
  function shutdown() {
    const deadline = setTimeout(() => process.exit(1), 10000);
    deadline.unref();
    server.close(async () => {
      await mongoose.disconnect();
      if (getRedisClient()?.isOpen) await getRedisClient().quit();
      process.exit(0);
    });
  }
  process.once('SIGTERM', shutdown);
  process.once('SIGINT', shutdown);
}
start().catch(() => {
  console.error('Application startup failed; check database and cache configuration.');
  process.exit(1);
});

export default app;
