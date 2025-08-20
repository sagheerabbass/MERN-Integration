const express = require('express');
const router = express.Router();
const Candidate = require('../models/Candidate');
const Log = require('../models/Log');
const { StatusCodes } = require('http-status-codes');

// POST /api/candidates - Create a new candidate (for Python service)
router.post('/', async (req, res) => {
  try {
    const {
      name,
      email,
      phone,
      skills,
      experience,
      resumeUrl,
      appliedPosition,
      score = 0,
      source = 'ai_intern'
    } = req.body;

    // Validate required fields
    if (!name || !email || !phone || !skills || !experience || !resumeUrl || !appliedPosition) {
      return res.status(StatusCodes.BAD_REQUEST).json({
        success: false,
        message: 'All required fields must be provided'
      });
    }

    // Check if candidate already exists
    const existingCandidate = await Candidate.findOne({ email });
    if (existingCandidate) {
      return res.status(StatusCodes.CONFLICT).json({
        success: false,
        message: 'Candidate with this email already exists',
        data: existingCandidate
      });
    }

    const candidate = await Candidate.create({
      name,
      email,
      phone,
      skills,
      experience,
      resumeUrl,
      appliedPosition,
      score,
      source
    });

    // Log the creation
    await Log.create({
      action: `Candidate ${name} created with position ${appliedPosition}`,
      candidate_id: candidate._id
    });

    res.status(StatusCodes.CREATED).json({
      success: true,
      message: 'Candidate created successfully',
      data: candidate
    });
  } catch (error) {
    console.error('Error creating candidate:', error);
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({
      success: false,
      message: 'Error creating candidate',
      error: error.message
    });
  }
});

// GET /api/candidates - Get all candidates with filtering
router.get('/', async (req, res) => {
  try {
    const { 
      domain, 
      status, 
      source, 
      minExperience, 
      maxExperience, 
      minScore, 
      maxScore,
      search,
      page = 1,
      limit = 10
    } = req.query;

    // Build filter object
    const filter = {};
    
    if (domain) filter.appliedPosition = { $regex: domain, $options: 'i' };
    if (status) filter.status = status;
    if (source) filter.source = source;
    if (minExperience) filter.experience = { $gte: parseInt(minExperience) };
    if (maxExperience) filter.experience = { ...filter.experience, $lte: parseInt(maxExperience) };
    if (minScore) filter.score = { $gte: parseInt(minScore) };
    if (maxScore) filter.score = { ...filter.score, $lte: parseInt(maxScore) };
    
    if (search) {
      filter.$or = [
        { name: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } },
        { appliedPosition: { $regex: search, $options: 'i' } }
      ];
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const candidates = await Candidate.find(filter)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit));

    const total = await Candidate.countDocuments(filter);

    res.json({
      success: true,
      data: {
        candidates,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / parseInt(limit))
        }
      }
    });
  } catch (error) {
    console.error('Error fetching candidates:', error);
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({
      success: false,
      message: 'Error fetching candidates',
      error: error.message
    });
  }
});

// PATCH /api/candidates/:id/status - Update candidate status
router.patch('/:id/status', async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    // Validate status
    const validStatuses = ['pending', 'shortlisted', 'rejected', 'interviewed', 'hired'];
    if (!validStatuses.includes(status)) {
      return res.status(StatusCodes.BAD_REQUEST).json({
        success: false,
        message: `Invalid status. Must be one of: ${validStatuses.join(', ')}`
      });
    }

    const candidate = await Candidate.findById(id);
    if (!candidate) {
      return res.status(StatusCodes.NOT_FOUND).json({
        success: false,
        message: 'Candidate not found'
      });
    }

    const oldStatus = candidate.status;
    candidate.status = status;
    await candidate.save();

    // Log the status change
    await Log.create({
      action: `Status updated from ${oldStatus} to ${status} for ${candidate.name}`,
      candidate_id: candidate._id
    });

    res.json({
      success: true,
      message: 'Status updated successfully',
      data: candidate
    });
  } catch (error) {
    console.error('Error updating status:', error);
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({
      success: false,
      message: 'Error updating status',
      error: error.message
    });
  }
});

// GET /api/candidates/:id - Get single candidate
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const candidate = await Candidate.findById(id);
    if (!candidate) {
      return res.status(StatusCodes.NOT_FOUND).json({
        success: false,
        message: 'Candidate not found'
      });
    }

    res.json({
      success: true,
      data: candidate
    });
  } catch (error) {
    console.error('Error fetching candidate:', error);
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({
      success: false,
      message: 'Error fetching candidate',
      error: error.message
    });
  }
});

// GET /api/candidates/stats - Get candidate statistics
router.get('/stats/overview', async (req, res) => {
  try {
    const totalCandidates = await Candidate.countDocuments();
    const shortlisted = await Candidate.countDocuments({ status: 'shortlisted' });
    const rejected = await Candidate.countDocuments({ status: 'rejected' });
    const pending = await Candidate.countDocuments({ status: 'pending' });
    const interviewed = await Candidate.countDocuments({ status: 'interviewed' });
    const hired = await Candidate.countDocuments({ status: 'hired' });

    const topPositions = await Candidate.aggregate([
      { $group: { _id: '$appliedPosition', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 5 }
    ]);

    const recentCandidates = await Candidate.find()
      .sort({ createdAt: -1 })
      .limit(5)
      .select('name email appliedPosition status createdAt');

    res.json({
      success: true,
      data: {
        total: totalCandidates,
        shortlisted,
        rejected,
        pending,
        interviewed,
        hired,
        topPositions,
        recentCandidates
      }
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({
      success: false,
      message: 'Error fetching stats',
      error: error.message
    });
  }
});

module.exports = router;
