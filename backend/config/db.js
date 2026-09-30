import mongoose from 'mongoose';
import { MONGODB_URI } from './utils.js';
export default async function connectDB() {
  try {
    await mongoose.connect(MONGODB_URI, { serverSelectionTimeoutMS: 10000 });
    console.log('MongoDB connected');
  } catch {
    // Connection strings may contain credentials; never log them.
    throw new Error('MongoDB connection failed');
  }
  mongoose.connection.on('error', () => console.error('MongoDB connection error'));
  return mongoose.connection;
}
