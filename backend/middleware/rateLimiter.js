const rateLimit = require('express-rate-limit');
const { log } = require('../utils/logger'); // Optional: for logging

// Configuration object for easy maintenance
const rateLimitConfig = {
  standard: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100,
    message: 'Too many requests from this IP, please try again later',
    headers: true,
    skipSuccessfulRequests: false
  },
  auth: {
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 5,
    message: 'Too many login attempts, please try again later',
    headers: true,
    skipSuccessfulRequests: true // Don't count successful logins
  },
  sensitive: {
    windowMs: 30 * 60 * 1000, // 30 minutes
    max: 10,
    message: 'Too many attempts on sensitive endpoint',
    headers: true
  }
};

// Custom handler for consistent error responses
const handler = (req, res, next, options) => {
  log.warn(`Rate limit exceeded for ${req.ip} on ${req.path}`);
  res.status(429).json({
    success: false,
    error: options.message,
    timestamp: new Date().toISOString(),
    path: req.path
  });
};

// Rate limiters with enhanced configuration
const apiLimiter = rateLimit({
  ...rateLimitConfig.standard,
  handler: (req, res) => handler(req, res, null, rateLimitConfig.standard)
});

const loginLimiter = rateLimit({
  ...rateLimitConfig.auth,
  handler: (req, res) => handler(req, res, null, rateLimitConfig.auth)
});

const sensitiveLimiter = rateLimit({
  ...rateLimitConfig.sensitive,
  handler: (req, res) => handler(req, res, null, rateLimitConfig.sensitive)
});

// Optional: Redis store for distributed environments
if (process.env.USE_REDIS === 'true') {
  const RedisStore = require('rate-limit-redis');
  const redisClient = require('../config/redis');
  
  const applyRedisStore = (config) => ({
    ...config,
    store: new RedisStore({
      sendCommand: (...args) => redisClient.sendCommand(args),
      prefix: 'rl:'
    })
  });

  apiLimiter = rateLimit(applyRedisStore(rateLimitConfig.standard));
  loginLimiter = rateLimit(applyRedisStore(rateLimitConfig.auth));
}

module.exports = {
  apiLimiter,
  loginLimiter,
  sensitiveLimiter,
  rateLimitConfig // Optional: export for testing
};