# Candidate Management API Documentation

## Base URL
All endpoints are prefixed with `/api`

## Authentication
Note: JWT middleware will be added by other developers. Currently, endpoints are open for development purposes.

## Endpoints

### 1. Create Candidate
**POST** `/api/candidates`

Creates a new candidate with the provided data.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "domain": "React",
  "interview_answers": ["Answer 1", "Answer 2", "Answer 3"]
}
```

**Required Fields:**
- `name` (string): Candidate's full name
- `email` (string): Candidate's email address (must be unique)
- `domain` (string): Candidate's domain (e.g., "React", "Python", "Node.js")

**Optional Fields:**
- `interview_answers` (array of strings): Answers to interview questions

**Response (201 Created):**
```json
{
  "message": "Candidate created successfully",
  "candidate": {
    "_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "domain": "React",
    "interview_answers": ["Answer 1", "Answer 2", "Answer 3"],
    "status": "New",
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `409 Conflict`: Email already exists
- `500 Internal Server Error`: Server error

### 2. Get All Candidates
**GET** `/api/candidates`

Fetches all candidates with optional filtering by domain and status.

**Query Parameters:**
- `domain` (optional): Filter by domain (e.g., "React", "Python")
- `status` (optional): Filter by status ("New", "Shortlisted", "Rejected")

**Example Requests:**
- `GET /api/candidates` - Get all candidates
- `GET /api/candidates?domain=React` - Get React candidates
- `GET /api/candidates?status=Shortlisted` - Get shortlisted candidates
- `GET /api/candidates?domain=Python&status=New` - Get new Python candidates

**Response (200 OK):**
```json
{
  "candidates": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "domain": "React",
      "interview_answers": ["Answer 1", "Answer 2"],
      "status": "New",
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ],
  "count": 1
}
```

### 3. Update Candidate Status
**PATCH** `/api/candidates/:id/status`

Updates a candidate's status.

**URL Parameters:**
- `id` (string): Candidate's MongoDB ObjectId

**Request Body:**
```json
{
  "status": "Shortlisted"
}
```

**Valid Status Values:**
- "New"
- "Shortlisted"
- "Rejected"

**Response (200 OK):**
```json
{
  "message": "Status updated successfully",
  "candidate": {
    "_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "domain": "React",
    "status": "Shortlisted",
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid status value
- `404 Not Found`: Candidate not found
- `500 Internal Server Error`: Server error

### 4. Get Action Logs
**GET** `/api/candidates/logs`

Retrieves all action logs with candidate details.

**Response (200 OK):**
```json
{
  "logs": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "action": "Status updated from New to Shortlisted for John Doe",
      "candidate_id": {
        "_id": "507f1f77bcf86cd799439011",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "domain": "React"
      },
      "timestamp": "2024-01-15T11:00:00.000Z"
    }
  ],
  "count": 1
}
```

### 5. Send WhatsApp Invite
**POST** `/api/candidates/:id/invite`

Sends a WhatsApp invite to a candidate via the Python service.

**URL Parameters:**
- `id` (string): Candidate's MongoDB ObjectId

**Response (200 OK):**
```json
{
  "message": "Invite triggered",
  "python_response": {
    "status": "success",
    "message": "WhatsApp invite sent successfully"
  }
}
```

**Error Responses:**
- `404 Not Found`: Candidate not found
- `500 Internal Server Error`: Server error

## Environment Variables

Create a `.env` file in the backend directory:

```bash
MONGO_URI=mongodb://localhost:27017/candidate_management
PORT=5000
PYTHON_SERVICE_URL=http://localhost:8000
JWT_SECRET=your-secret-key
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Descriptive error message"
}
```

## Testing the APIs

### Using cURL:

```bash
# Create a candidate
curl -X POST http://localhost:5000/api/candidates \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","domain":"React"}'

# Get all candidates
curl http://localhost:5000/api/candidates

# Get filtered candidates
curl "http://localhost:5000/api/candidates?domain=React&status=New"

# Update status
curl -X PATCH http://localhost:5000/api/candidates/507f1f77bcf86cd799439011/status \
  -H "Content-Type: application/json" \
  -d '{"status":"Shortlisted"}'

# Get logs
curl http://localhost:5000/api/candidates/logs
```

### Using Postman:
Import the following collection structure:
- Base URL: `http://localhost:5000/api`
- Endpoints as listed above
