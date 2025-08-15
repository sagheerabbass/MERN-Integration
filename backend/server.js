const express = require('express')
const dotenv = require('dotenv')
dotenv.config()
const mongoose = require('mongoose');
const candidatesRoute = require('./routes/candidateRoutes');

const app = express();
app.use(express.json());

// MongoDB connection with better error handling
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/candidate_management';

mongoose.connect(MONGO_URI)
  .then(() => console.log('✅ MongoDB Connected successfully'))
  .catch(err => {
    console.error('❌ MongoDB connection error:', err.message);
    console.log('💡 Make sure MongoDB is running and MONGO_URI is set in .env file');
    console.log('💡 Using default: mongodb://localhost:27017/candidate_management');
  });

// Routes
app.use('/api/candidates', candidatesRoute);

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
