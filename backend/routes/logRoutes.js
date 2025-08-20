const express = require('express');
const router = express.Router();
const Log = require('../models/Log');
const { StatusCodes } = require('http-status-codes');

// GET /api/logs - Retrieve all action logs with filtering
router.get('/', async (req, res) => {
  try {
    const { 
      action, 
      candidateId, 
      startDate, 
      endDate, 
      page = 1, 
      limit = 50 
    } = req.query;

    // Build filter object
    const filter = {};
    
    if (action) filter.action = { $regex: action, $options: 'i' };
    if (candidateId) filter.candidate_id = candidateId;
    
    if (startDate || endDate) {
      filter.createdAt = {};
      if (startDate) filter.createdAt.$gte = new Date(startDate);
      if (endDate) filter.createdAt.$lte = new Date(endDate);
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const logs = await Log.find(filter)
      .populate('candidate_id', 'name email domain') // pick only needed fields
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit));

    const total = await Log.countDocuments(filter);

    res.json({
      success: true,
      data: {
        logs,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / parseInt(limit))
        }
      }
    });
  } catch (err) {
    console.error('Error fetching logs:', err);
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ 
      success: false, 
      message: 'Error fetching logs' 
    });
  }
});

module.exports = router;
