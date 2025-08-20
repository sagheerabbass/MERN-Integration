const express = require('express');
const axios = require('axios');
const Candidate = require('../models/Candidate');
const Log = require('../models/Log');

const router = express.Router();

// POST /api/candidates - Create a new candidate
router.post('/', async (req, res) => {
  try {
    // Call Python automation (no request body required now)
    const pythonResponse = await axios.post(
      `${process.env.PYTHON_SERVICE_URL}/run-workflow`,
      {},
      { headers: { 'Authorization': `Bearer ${process.env.JWT_SECRET}` } }
    );

    const workflowCandidate = pythonResponse.data.candidate;

    if (!workflowCandidate || !workflowCandidate.email) {
      return res.status(400).json({ error: 'No candidate data returned from workflow' });
    }

    // Prevent duplicate candidates
    const existingCandidate = await Candidate.findOne({ email: workflowCandidate.email });
    if (existingCandidate) {
      return res.status(409).json({ error: 'Candidate already exists' });
    }

    // Save candidate in MongoDB
    const candidate = new Candidate(workflowCandidate);
    await candidate.save();

    // Log the automation action
    await Log.create({
      action: `Candidate ${candidate.name} processed via automation (domain: ${candidate.domain})`,
      candidate_id: candidate._id
    });

    res.status(201).json({
      message: 'Candidate created and processed successfully',
      candidate
    });
  } catch (error) {
    console.error('Error in workflow candidate creation:', error.message || error);
    res.status(500).json({ error: 'Server error while creating candidate with workflow' });
  }
});


// GET /api/candidates - Fetch all candidates with optional filtering
router.get('/', async (req, res) => {
  try {
    const { domain, status } = req.query;
    
    // Build filter object
    const filter = {};
    if (domain) filter.domain = domain;
    if (status) filter.status = status;

    const candidates = await Candidate.find(filter)
      .sort({ created_at: -1 });

    res.json({
      candidates,
      count: candidates.length
    });
  } catch (error) {
    console.error('Error fetching candidates:', error);
    res.status(500).json({ error: 'Server error while fetching candidates' });
  }
});

// PATCH /api/candidates/:id/status - Update candidate status
router.patch('/:id/status', async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    // Validate status
    const validStatuses = ['New', 'Shortlisted', 'Rejected'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ 
        error: 'Invalid status. Must be one of: New, Shortlisted, Rejected' 
      });
    }

    const candidate = await Candidate.findById(id);
    if (!candidate) {
      return res.status(404).json({ error: 'Candidate not found' });
    }

    // Update status
    const oldStatus = candidate.status;
    candidate.status = status;
    await candidate.save();

    // Log the status change
    await Log.create({
      action: `Status updated from ${oldStatus} to ${status} for ${candidate.name}`,
      candidate_id: candidate._id
    });

    res.json({
      message: 'Status updated successfully',
      candidate
    });
  } catch (error) {
    console.error('Error updating status:', error);
    res.status(500).json({ error: 'Server error while updating status' });
  }
});

// GET /api/logs - Retrieve all action logs
router.get('/logs', async (req, res) => {
  try {
    const logs = await Log.find()
      .populate('candidate_id', 'name email domain')
      .sort({ timestamp: -1 });

    res.json({
      logs,
      count: logs.length
    });
  } catch (error) {
    console.error('Error fetching logs:', error);
    res.status(500).json({ error: 'Server error while fetching logs' });
  }
});

// POST /api/candidates/:id/invite - Send WhatsApp invite (existing endpoint)
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
