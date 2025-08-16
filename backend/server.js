// server.js
// This is the updated server file that integrates authentication with your existing routes.

const express = require('express');
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const cors = require("cors");
// Added new required packages for authentication
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Existing route files
const candidatesRoute = require('./routes/candidateRoutes');
const logRoutes = require('./routes/logRoutes');


dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());

// MongoDB connection with better error handling
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/candidate_management';

mongoose.connect(MONGO_URI)
  .then(() => console.log('✅ MongoDB Connected successfully'))
  .catch(err => {
    console.error('❌ MongoDB connection error:', err.message);
    console.log('💡 Make sure MongoDB is running and MONGO_URI is set in .env file');
    console.log('💡 Using default: mongodb://localhost:27017/candidate_management');
    // Exit process with failure
    process.exit(1);
  });

// MongoDB Schema and Model
// We define a simple User schema with email and password fields.
const UserSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});

const User = mongoose.model('User', UserSchema);

// JWT Secret from .env file.
const jwtSecret = process.env.JWT_SECRET;

// Middleware to protect routes.
// This middleware checks for a valid JWT in the request headers.
const authMiddleware = (req, res, next) => {
  // Get token from header
  const token = req.header('x-auth-token');

  // Check if no token
  if (!token) {
    return res.status(401).json({ message: 'No token, authorization denied' });
  }

  // Verify token
  try {
    const decoded = jwt.verify(token, jwtSecret);
    req.user = decoded.user;
    next();
  } catch (err) {
    res.status(401).json({ message: 'Token is not valid' });
  }
};

// Seeding the database with an initial user for testing.
// This is for demonstration purposes. In a real app, this user would be created via a registration flow.
const seedAdminUser = async () => {
  const existingUser = await User.findOne({ email: 'admin@example.com' });
  if (!existingUser) {
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash('password123', salt);
    const adminUser = new User({
      email: 'admin@example.com',
      password: hashedPassword,
    });
    await adminUser.save();
    console.log('Admin user seeded successfully.');
  }
};

// Seed the database when the server starts.
seedAdminUser();

// API Routes
// Login Route: /api/auth/login
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    // Check if user exists
    let user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid Credentials' });
    }

    // Check if password matches
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid Credentials' });
    }

    // Create and sign a JWT
    const payload = {
      user: {
        id: user.id,
      },
    };

    jwt.sign(
      payload,
      jwtSecret,
      { expiresIn: '1h' }, // Token expires in 1 hour
      (err, token) => {
        if (err) throw err;
        res.json({ token });
      }
    );
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// Routes
// We've applied the authMiddleware to protect these routes.
app.use('/api/candidates', authMiddleware, candidatesRoute);
app.use('/api/logs', authMiddleware, logRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    mongo_connected: mongoose.connection.readyState === 1
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
