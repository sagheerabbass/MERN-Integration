# AI Intern Backend API Integration Guide

This guide provides comprehensive documentation for integrating the AI Intern system with the MERN dashboard backend APIs.

## 🎯 Overview

The backend APIs serve as a bridge between:
- **AI Intern Python Service** → Pushes candidate data
- **MERN Dashboard** → Displays and manages candidates

## 📋 API Endpoints

### 1. Create Candidate (For Python Service)
**POST** `/api/v1/candidates`

**Headers:**
```
Authorization: Bearer <python-service-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "skills": ["JavaScript", "React", "Node.js"],
  "experience": 3,
  "resumeUrl": "https://example.com/resumes/john-doe.pdf",
  "appliedPosition": "Frontend Developer",
  "score": 85,
  "source": "ai_intern"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Candidate created successfully",
  "data": {
    "_id": "candidate_id",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "status": "pending",
    "createdAt": "2024-01-01T00:00:00.000Z"
  }
}
```

### 2. Get All Candidates (For Dashboard)
**GET** `/api/v1/candidates`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `status` - Filter by status (pending, shortlisted, rejected, interviewed, hired)
- `source` - Filter by source (linkedin, indeed, referral, direct, ai_intern)
- `minExperience` - Minimum years of experience
- `maxExperience` - Maximum years of experience
- `minScore` - Minimum score
- `maxScore` - Maximum score
- `search` - Search in name, email, or position
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 10)

**Example:**
```
GET /api/v1/candidates?status=shortlisted&minExperience=2&page=1&limit=20
```

**Response:**
```json
{
  "success": true,
  "data": {
    "candidates": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

### 3. Update Candidate Status (For Dashboard)
**PATCH** `/api/v1/candidates/:id/status`

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "shortlisted"
}
```

**Valid Status Values:** `pending`, `shortlisted`, `rejected`, `interviewed`, `hired`

**Response:**
```json
{
  "success": true,
  "message": "Status updated successfully",
  "data": {
    "_id": "candidate_id",
    "name": "John Doe",
    "status": "shortlisted",
    "updatedAt": "2024-01-01T00:00:00.000Z"
  }
}
```

### 4. Get Single Candidate (For Dashboard)
**GET** `/api/v1/candidates/:id`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "candidate_id",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "skills": ["JavaScript", "React", "Node.js"],
    "experience": 3,
    "resumeUrl": "https://example.com/resumes/john-doe.pdf",
    "appliedPosition": "Frontend Developer",
    "status": "shortlisted",
    "score": 85,
    "interviewAnswers": [...],
    "notes": "Great candidate",
    "createdAt": "2024-01-01T00:00:00.000Z"
  }
}
```

### 5. Get Candidate Statistics (For Dashboard)
**GET** `/api/v1/candidates/stats/overview`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 150,
    "shortlisted": 45,
    "rejected": 30,
    "pending": 60,
    "interviewed": 10,
    "hired": 5,
    "topPositions": [
      { "_id": "Frontend Developer", "count": 25 },
      { "_id": "Backend Developer", "count": 20 }
    ],
    "recentCandidates": [...]
  }
}
```

### 6. Get Action Logs (For Dashboard)
**GET** `/api/v1/logs`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `action` - Filter by action text
- `candidateId` - Filter by candidate ID
- `startDate` - Filter by start date (YYYY-MM-DD)
- `endDate` - Filter by end date (YYYY-MM-DD)
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 50)

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "_id": "log_id",
        "action": "Status updated from pending to shortlisted for John Doe",
        "candidate_id": {
          "_id": "candidate_id",
          "name": "John Doe",
          "email": "john.doe@example.com"
        },
        "createdAt": "2024-01-01T00:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 200,
      "pages": 4
    }
  }
}
```

## 🔐 Authentication

### Python Service Authentication
The Python service uses a special token for authentication:
```python
import requests

headers = {
    'Authorization': f'Bearer {PYTHON_SERVICE_TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:5000/api/v1/candidates',
    json=candidate_data,
    headers=headers
)
```

### Dashboard Authentication
The dashboard uses JWT tokens:
```javascript
// React example
const token = localStorage.getItem('token');

const response = await axios.get('http://localhost:5000/api/v1/candidates', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## 🔄 Integration Examples

### Python Service Integration
```python
import requests
import json

def send_candidate_to_backend(candidate_data):
    """Send candidate data from AI Intern to backend"""
    
    backend_url = "http://localhost:5000/api/v1/candidates"
    headers = {
        'Authorization': f'Bearer {os.getenv("PYTHON_SERVICE_TOKEN")}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(backend_url, json=candidate_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending candidate to backend: {e}")
        return None
```

### React Dashboard Integration
```javascript
// services/candidateService.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/v1';

const candidateService = {
  // Get all candidates with filters
  getCandidates: async (filters = {}) => {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/candidates`, {
      params: filters,
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Update candidate status
  updateCandidateStatus: async (id, status) => {
    const token = localStorage.getItem('token');
    const response = await axios.patch(
      `${API_BASE_URL}/candidates/${id}/status`,
      { status },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  },

  // Get candidate statistics
  getStats: async () => {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/candidates/stats/overview`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Get action logs
  getLogs: async (filters = {}) => {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/logs`, {
      params: filters,
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  }
};

export default candidateService;
```

## 🚀 Getting Started

1. **Start the backend server:**
   ```bash
   cd backend
   npm install
   npm start
   ```

2. **Set environment variables:**
   ```bash
   MONGO_URI=mongodb://localhost:27017/candidate_management
   JWT_SECRET=your_jwt_secret
   PYTHON_SERVICE_TOKEN=your_python_service_token
   FRONTEND_URL=http://localhost:3000
   ```

3. **Test the APIs:**
   ```bash
   # Test candidate creation (Python service)
   curl -X POST http://localhost:5000/api/v1/candidates \
     -H "Authorization: Bearer <python-service-token>" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","email":"test@example.com","phone":"123","skills":["test"],"experience":2,"resumeUrl":"test","appliedPosition":"Developer"}'

   # Test candidate fetching (Dashboard)
   curl -X GET http://localhost:5000/api/v1/candidates \
     -H "Authorization: Bearer <jwt-token>"
   ```

## 📊 Data Flow

```
AI Intern Python Service
        ↓ POST /api/v1/candidates
Backend APIs (Node.js + Express)
        ↓ MongoDB Atlas
MERN Dashboard (React)
        ↓ GET /api/v1/candidates
        ↓ PATCH /api/v1/candidates/:id/status
        ↓ GET /api/v1/logs
```

## 🔧 Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error message",
  "error": "Detailed error information"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error
