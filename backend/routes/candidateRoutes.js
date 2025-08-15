const express = require('express');
const axios = require('axios');
const Candidate = require('../models/Candidate');
const Log = require('../models/Log');

const router = express.Router();

router.post('/:id/invite', async (req, res) => {
  try {
    const candidate = await Candidate.findById(req.params.id);
    if (!candidate) return res.status(404).json({ error: 'Candidate not found' });

    // Send request to Python service
    const pythonResponse = await axios.post(
      `${process.env.PYTHON_SERVICE_URL}/send-invite`,
      { email: candidate.email, name: candidate.name, domain: candidate.domain },
      { headers: { 'Authorization': `Bearer ${process.env.JWT_SECRET}` } } // optional security
    );

    // Log the action
    await Log.create({
      action: `WhatsApp invite sent to ${candidate.name}`,
      candidate_id: candidate._id
    });

    res.json({ message: 'Invite triggered', python_response: pythonResponse.data });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
