import express from 'express';
import cors from 'express-cors';
import dotenv from 'dotenv';
import authRoutes from './routes/auth.js';
import { query } from './config/database.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(cors());

// Routes
app.use('/api/auth', authRoutes);

// Health check
app.get('/api/health', async (req, res) => {
  try {
    const result = await query('SELECT NOW()');
    res.json({
      status: 'ok',
      timestamp: result.rows[0].now,
      message: 'Backend is running'
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: 'Database connection failed'
    });
  }
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📝 API available at http://localhost:${PORT}/api`);
});
