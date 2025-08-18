class UnauthorizedError extends Error {
  constructor(message) {
    super(message);
    this.statusCode = 403; // 403 = forbidden
  }
}

module.exports = UnauthorizedError;
