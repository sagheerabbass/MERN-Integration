// Simple test script to verify API endpoints
const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api';

async function testAPIs() {
  console.log('🧪 Testing Candidate Management APIs...\n');

  try {
    // Test 1: Create a candidate
    console.log('1. Creating a new candidate...');
    const newCandidate = {
      name: 'Test User',
      email: 'test@example.com',
      domain: 'React',
      interview_answers: ['I love React', '2 years experience', 'Redux, Hooks']
    };
    
    const createResponse = await axios.post(`${BASE_URL}/candidates`, newCandidate);
    console.log('✅ Candidate created:', createResponse.data.candidate._id);
    const candidateId = createResponse.data.candidate._id;

    // Test 2: Get all candidates
    console.log('\n2. Fetching all candidates...');
    const allCandidates = await axios.get(`${BASE_URL}/candidates`);
    console.log(`✅ Found ${allCandidates.data.count} candidates`);

    // Test 3: Filter candidates by domain
    console.log('\n3. Filtering React candidates...');
    const reactCandidates = await axios.get(`${BASE_URL}/candidates?domain=React`);
    console.log(`✅ Found ${reactCandidates.data.count} React candidates`);

    // Test 4: Update candidate status
    console.log('\n4. Updating candidate status...');
    const updateResponse = await axios.patch(
      `${BASE_URL}/candidates/${candidateId}/status`,
      { status: 'Shortlisted' }
    );
    console.log('✅ Status updated to:', updateResponse.data.candidate.status);

    // Test 5: Get logs
    console.log('\n5. Fetching action logs...');
    const logs = await axios.get(`${BASE_URL}/candidates/logs`);
    console.log(`✅ Found ${logs.data.count} log entries`);

    console.log('\n🎉 All API tests completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  testAPIs();
}

module.exports = { testAPIs };
