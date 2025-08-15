const mongoose = require('mongoose');

const logSchema = new mongoose.Schema({
  action: String, // e.g. "Invite sent"
  candidate_id: mongoose.Schema.Types.ObjectId,
  timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Log', logSchema);
