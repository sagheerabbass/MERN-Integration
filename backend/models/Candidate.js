const mongoose = require('mongoose');

const candidateSchema = new mongoose.Schema({
  name: String,
  email: String,
  domain: String,
  interview_answers: [String],
  status: { type: String, enum: ["New", "Shortlisted", "Rejected"], default: "New" },
  created_at: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Candidate', candidateSchema);
