"""
AI Intern Backend Integration Module

This module provides functions to send candidate data from the AI Intern system
to the MERN backend APIs.
"""

import requests
import json
import os
from typing import Dict, Any, Optional

class BackendIntegration:
    def __init__(self, base_url: str = None, api_token: str = None):
        """
        Initialize the backend integration
        
        Args:
            base_url: Backend API base URL (defaults to env var BACKEND_URL)
            api_token: API token for authentication (defaults to env var PYTHON_SERVICE_TOKEN)
        """
        self.base_url = base_url or os.getenv('BACKEND_URL', 'http://localhost:5000/api/v1')
        self.api_token = api_token or os.getenv('PYTHON_SERVICE_TOKEN')
        
        if not self.api_token:
            raise ValueError("PYTHON_SERVICE_TOKEN environment variable is required")
    
    def send_candidate(self, candidate_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send candidate data to backend
        
        Args:
            candidate_data: Dictionary containing candidate information
            
        Returns:
            Response data from backend or None if error
        """
        endpoint = f"{self.base_url}/candidates"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'skills', 'experience', 'resumeUrl', 'appliedPosition']
        missing_fields = [field for field in required_fields if field not in candidate_data]
        
        if missing_fields:
            print(f"Missing required fields: {missing_fields}")
            return None
        
        try:
            response = requests.post(endpoint, json=candidate_data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Candidate sent successfully: {result['data']['_id']}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending candidate to backend: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def send_batch_candidates(self, candidates_list: list) -> list:
        """
        Send multiple candidates to backend
        
        Args:
            candidates_list: List of candidate dictionaries
            
        Returns:
            List of results for each candidate
        """
        results = []
        
        for candidate in candidates_list:
            result = self.send_candidate(candidate)
            results.append({
                'candidate': candidate,
                'success': result is not None,
                'response': result
            })
        
        return results
    
    def check_backend_health(self) -> bool:
        """
        Check if backend is healthy
        
        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

# Usage examples
if __name__ == "__main__":
    # Initialize integration
    integration = BackendIntegration()
    
    # Check backend health
    if integration.check_backend_health():
        print("✅ Backend is healthy")
    else:
        print("❌ Backend is not accessible")
    
    # Example candidate data
    candidate = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567890",
        "skills": ["Python", "Django", "PostgreSQL", "AWS"],
        "experience": 4,
        "resumeUrl": "https://example.com/resumes/jane-smith.pdf",
        "appliedPosition": "Backend Developer",
        "score": 92,
        "source": "ai_intern"
    }
    
    # Send candidate
    result = integration.send_candidate(candidate)
    if result:
        print("Candidate successfully sent to backend")
    else:
        print("Failed to send candidate")
