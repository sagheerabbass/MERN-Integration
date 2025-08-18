
const express = require('express');
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const hpp = require('hpp');
// const mongoSanitize = require('express-mongo-sanitize');
const { filterXSS } = require('xss');
const morgan = require('morgan');
const bcrypt = require('bcryptjs');

// Load environment variables
dotenv.config();

const app = express();

// ------------------ IMPORT MIDDLEWARES ------------------
const auth = require('./middleware/auth');
const pythonServiceAuth = require('./middleware/pythonServiceAuth');
const rateLimiter = require('./middleware/rateLimiter');

// ------------------ IMPORT ROUTES ------------------
const candidatesRoute = require('./routes/candidateRoutes');
const logRoutes = require('./routes/logRoutes');
const authRoutes = require('./routes/authRoutes');

// ------------------ IMPORT MODELS ------------------
const User = require('./models/User');

// ------------------ DATABASE CONNECTION ------------------
const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/candidate_management', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 5000,
    });
    console.log('✅ MongoDB Connected successfully');
    await seedAdminUser();
  } catch (err) {
    console.error('❌ MongoDB connection error:', err.message);
    process.exit(1);
  }
};

// ------------------ MIDDLEWARE ------------------
app.use(morgan('combined'));
app.use(express.json({ limit: '10kb' }));
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

// Security middleware
app.use(helmet());
app.use(hpp());
// app.use(mongoSanitize());

// Use centralized rate limiter from middleware
const { apiLimiter } = require('./middleware/rateLimiter');
app.use('/api', apiLimiter);

// XSS protection
app.use((req, res, next) => {
  const xssOptions = {
    whiteList: {},
    stripIgnoreTag: true,
    stripIgnoreTagBody: ['script']
  };

  try {
    ['body', 'query', 'params'].forEach(key => {
      if (req[key]) {
        Object.keys(req[key]).forEach(prop => {
          if (typeof req[key][prop] === 'string') {
            req[key][prop] = filterXSS(req[key][prop], xssOptions);
          }
        });
      }
    });
    next();
  } catch (err) {
    console.error('XSS Sanitization Error:', err);
    next();
  }
});

// ------------------ SEED ADMIN ------------------
const seedAdminUser = async () => {
  if (process.env.NODE_ENV !== 'production') {
    const existingUser = await User.findOne({ email: 'admin@example.com' });
    if (!existingUser) {
      const hashedPassword = await bcrypt.hash(
        process.env.ADMIN_DEFAULT_PASSWORD || 'password123',
        12
      );
      await User.create({
        email: 'admin@example.com',
        password: hashedPassword
      });
      console.log('🔐 Admin user seeded');
    }
  }
};

// ------------------ ROUTES ------------------
// Public routes
app.use('/api/v1/auth', authRoutes);

// Protected routes (require JWT auth)
app.use('/api/v1/candidates', auth, candidatesRoute);
app.use('/api/v1/logs', auth, logRoutes);

// Python service route
app.use('/api/v1/python-service', pythonServiceAuth, (req, res) => {
  res.json({ success: true, message: 'Python service accessed' });
});

// Health check
app.get('/api/v1/health', (req, res) => {
  res.status(200).json({
    success: true,
    data: {
      status: 'OK',
      timestamp: new Date().toISOString(),
      database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
      uptime: process.uptime(),
      memoryUsage: process.memoryUsage()
    }
  });
});

// ------------------ ERROR HANDLING ------------------
app.use((err, req, res, next) => {
  console.error(`[${new Date().toISOString()}] Error:`, err.stack);

  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  res.status(statusCode).json({
    success: false,
    error: message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Resource not found'
  });
});

// ------------------ SERVER STARTUP ------------------
const PORT = process.env.PORT || 5000;
const startServer = async () => {
  await connectDB();
  app.listen(PORT, () => {
    console.log(`🚀 Server running in ${process.env.NODE_ENV || 'development'} mode on port ${PORT}`);
    console.log(`📄 API Docs: http://localhost:${PORT}/api/v1/docs`);
  });
};

startServer();
