const express = require('express')
const dotenv = require('dotenv')
dotenv.config()
const mongoose = require('mongoose');
const candidatesRoute = require('./routes/candidateRoutes');

const app = express();
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.error(err));

// Routes
app.use('/api/candidates', candidatesRoute);

app.listen(process.env.PORT, () => console.log(`Server running on port ${process.env.PORT}`));
