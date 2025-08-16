const express = require('express');
const axios = require('axios');
const Log = require('../models/Log');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
   const logs = await Log.find()
  .populate('candidate_id', 'name email domain') // pick only needed fields
  .sort({ timestamp: -1 });
    res.json({ success: true, logs });
  } catch (err) {
    console.error('Error fetching logs:', err);
    res.status(500).json({ success: false, message: 'Error fetching logs' });
  }
});

module.exports = router;
