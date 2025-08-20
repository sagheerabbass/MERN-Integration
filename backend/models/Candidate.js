const mongoose = require('mongoose');

const candidateSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please provide candidate name'],
    trim: true,
    maxlength: [50, 'Name cannot be more than 50 characters']
  },
  email: {
    type: String,
    required: [true, 'Please provide email'],
    match: [
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
      'Please provide valid email'
    ],
    unique: true
  },
  phone: {
    type: String,
    required: [true, 'Please provide phone number']
  },
  skills: [{
    type: String,
    required: true
  }],
  experience: {
    type: Number,
    required: [true, 'Please provide years of experience'],
    min: [0, 'Experience cannot be negative']
  },
  resumeUrl: {
    type: String,
    required: [true, 'Please provide resume URL']
  },
  status: {
    type: String,
    enum: ['pending', 'shortlisted', 'rejected', 'interviewed', 'hired'],
    default: 'pending'
  },
  appliedPosition: {
    type: String,
    required: [true, 'Please provide applied position']
  },
  source: {
    type: String,
    enum: ['linkedin', 'indeed', 'referral', 'direct', 'ai_intern'],
    default: 'direct'
  },
  score: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },
  interviewAnswers: [{
    question: String,
    answer: String,
    score: Number
  }],
  notes: {
    type: String,
    maxlength: [500, 'Notes cannot be more than 500 characters']
  },
  interviewDate: {
    type: Date
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update the updatedAt field before saving
candidateSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Update the updatedAt field before updating
candidateSchema.pre('findOneAndUpdate', function(next) {
  this.set({ updatedAt: Date.now() });
  next();
});

module.exports = mongoose.model('Candidate', candidateSchema);
