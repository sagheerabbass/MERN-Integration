const { UnauthorizedError } = require('../errors');

const pythonServiceAuth = (req, res, next) => {
  const serviceToken = req.headers['x-service-token'];
  
  if (!serviceToken || serviceToken !== process.env.PYTHON_SERVICE_SECRET) {
    throw new UnauthorizedError('Service access denied');
  }
  
  next();
};

module.exports = pythonServiceAuth;