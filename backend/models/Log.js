const mongoose = require('mongoose');

const logSchema = new mongoose.Schema({
  action: String, // e.g. "Invite sent"
    candidate_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Candidate' }, // add ref
  timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Log', logSchema);
