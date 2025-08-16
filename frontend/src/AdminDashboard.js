import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
const AdminDashboard = () => {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [filter, setFilter] = useState({ name: '', domain: '', status: '' });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentCandidate, setCurrentCandidate] = useState(null);
  const [actionLogs, setActionLogs] = useState([]);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [editedAnswers, setEditedAnswers] = useState('');

  // Fetch candidates and logs on mount
  useEffect(() => {
    axios
      .get('http://localhost:5000/api/candidates')
      .then(response => {
        setCandidates(response.data.candidates || []);
        setFilteredCandidates(response.data.candidates || []);
      })
      .catch(error => console.error('Error fetching candidates:', error));

    axios
      .get('http://localhost:5000/api/logs')
      .then(response => setActionLogs(response.data.logs || []))
      .catch(error => console.error('Error fetching logs:', error));
  }, []);

  // Filter candidates based on input
  useEffect(() => {
    const filtered = candidates.filter(
      candidate =>
        candidate.name.toLowerCase().includes(filter.name.toLowerCase()) &&
        (filter.domain === '' || candidate.domain === filter.domain) &&
        (filter.status === '' || candidate.status === filter.status),
    );
    setFilteredCandidates(filtered);
  }, [filter, candidates]);

  const handleFilterChange = e => {
    const { name, value } = e.target;
    setFilter(prev => ({ ...prev, [name]: value }));
  };

  const openModal = (candidate = null) => {
    setCurrentCandidate(candidate);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setCurrentCandidate(null);
    setIsModalOpen(false);
  };

  const openDetailsModal = candidate => {
    setCurrentCandidate(candidate);
    setEditedAnswers(candidate.interview_answers?.join(', ') || '');
    setIsDetailsModalOpen(true);
  };

  const closeDetailsModal = () => {
    setCurrentCandidate(null);
    setEditedAnswers('');
    setIsDetailsModalOpen(false);
  };

  const handleSave = candidateData => {
    if (currentCandidate) {
      // Update candidate status
      axios
        .patch(`http://localhost:5000/api/candidates/${currentCandidate._id}/status`, { status: candidateData.status })
        .then(response => {
          setCandidates(
            candidates.map(c =>
              c._id === currentCandidate._id ? response.data.candidate : c,
            ),
          );
          fetchLogs();
        })
        .catch(error => console.error('Error updating candidate:', error));
    } else {
      // Add new candidate
      axios
        .post('http://localhost:5000/api/candidates', {
          name: candidateData.name,
          email: candidateData.email,
          domain: candidateData.domain,
          interview_answers: candidateData.interview_answers
            ? candidateData.interview_answers.split(',').map(answer => answer.trim())
            : [],
             status: candidateData.status,
        })
        .then(response => {
          setCandidates([...candidates, response.data.candidate]);
          console.log(response.data)
          fetchLogs();
        })
        .catch(error => console.error('Error adding candidate:', error));
    }
    closeModal();
  };

  const handleShortlist = id => {
    axios
      .patch(`http://localhost:5000/api/candidates/${id}/status`, { status: 'Shortlisted' })
      .then(response => {
        setCandidates(candidates.map(c => (c._id === id ? response.data.candidate : c)));
        fetchLogs();
      })
      .catch(error => console.error('Error shortlisting candidate:', error));
  };

  const handleReject = id => {
    axios
      .patch(`http://localhost:5000/api/candidates/${id}/status`, { status: 'Rejected' })
      .then(response => {
        setCandidates(candidates.map(c => (c._id === id ? response.data.candidate : c)));
        fetchLogs();
      })
      .catch(error => console.error('Error rejecting candidate:', error));
  };

  const handleInvite = id => {
    axios
      .post(`http://localhost:5000/api/candidates/${id}/invite`)
      .then(response => {
        alert(response.data.message || 'WhatsApp invite sent successfully!');
        fetchLogs();
      })
      .catch(error => console.error('Error sending invite:', error));
  };

  const fetchLogs = () => {
    axios
      .get('http://localhost:5000/api/logs')
      .then(response => setActionLogs(response.data.logs || []))
      .catch(error => console.error('Error fetching logs:', error));
  };

  const handleSaveAnswers = () => {
    if (currentCandidate) {
      const updatedAnswers = editedAnswers.split(',').map(answer => answer.trim());
      axios
        .patch(`http://localhost:5000/api/candidates/${currentCandidate._id}`, { interview_answers: updatedAnswers })
        .then(response => {
          setCandidates(
            candidates.map(c =>
              c._id === currentCandidate._id ? response.data.candidate : c,
            ),
          );
          closeDetailsModal();
        })
        .catch(error => console.error('Error updating interview answers:', error));
    }
  };
    const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="container mx-auto p-4">
       <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Admin Dashboard - Candidate Management</h1>
        <button
          onClick={handleLogout}
          className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
        >
          Logout
        </button>
      </div>
      {/* <h1 className="text-2xl font-bold mb-4">Admin Dashboard - Candidate Management</h1> */}

      {/* Filter Section */}
      <div className="mb-4 p-4 bg-gray-100 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            name="name"
            value={filter.name}
            onChange={handleFilterChange}
            placeholder="Filter by name"
            className="border-2 border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            name="domain"
            value={filter.domain}
            onChange={handleFilterChange}
            className="border-2 border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Domains</option>
            <option value="React">React</option>
            <option value="Python">Python</option>
            <option value="Node.js">Node.js</option>
          </select>
          <select
            name="status"
            value={filter.status}
            onChange={handleFilterChange}
            className="border-2 border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="New">New</option>
            <option value="Shortlisted">Shortlisted</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Add Candidate Button */}
      <button
        onClick={() => openModal()}
        className="mb-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
      >
        Add Candidate
      </button>

      {/* Candidates Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse bg-white shadow-md rounded-lg">
          <thead>
            <tr className="bg-gray-200">
              <th className="border p-2 text-left">Name</th>
              <th className="border p-2 text-left">Email</th>
              <th className="border p-2 text-left">Domain</th>
              <th className="border p-2 text-left">Status</th>
              <th className="border p-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCandidates.map(candidate => (
              <tr key={candidate._id} className="hover:bg-gray-100">
                <td className="border p-2">{candidate.name}</td>
                <td className="border p-2">{candidate.email}</td>
                <td className="border p-2">{candidate.domain}</td>
                <td className="border p-2">{candidate.status}</td>
                <td className="border p-2 space-x-2">
                  <button
                    onClick={() => handleShortlist(candidate._id)}
                    className="bg-green-500 text-white px-2 py-1 rounded-lg hover:bg-green-600 transition duration-200"
                  >
                    Shortlist
                  </button>
                  <button
                    onClick={() => handleReject(candidate._id)}
                    className="bg-red-500 text-white px-2 py-1 rounded-lg hover:bg-red-600 transition duration-200"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => openDetailsModal(candidate)}
                    className="bg-blue-500 text-white px-2 py-1 rounded-lg hover:bg-blue-600 transition duration-200"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => handleInvite(candidate._id)}
                    className="bg-teal-500 text-white px-2 py-1 rounded-lg hover:bg-teal-600 transition duration-200"
                  >
                    Send WhatsApp Invite
                  </button>
                  <button
                    onClick={() => openModal(candidate)}
                    className="bg-yellow-500 text-white px-2 py-1 rounded-lg hover:bg-yellow-600 transition duration-200"
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Action Logs Table */}
      <h2 className="text-xl font-bold mt-8 mb-4">Action Logs</h2>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse bg-white shadow-md rounded-lg">
          <thead>
            <tr className="bg-gray-200">
              <th className="border p-2 text-left">Timestamp</th>
              <th className="border p-2 text-left">Action</th>
              <th className="border p-2 text-left">Candidate</th>
              <th className="border p-2 text-left">Details</th>
            </tr>
          </thead>
          <tbody>
            {actionLogs.map(log => (
              <tr key={log._id} className="hover:bg-gray-100">
                <td className="border p-2">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="border p-2">{log.action}</td>
                <td className="border p-2">{log.candidate_id?.name || 'Unknown'}</td>
                <td className="border p-2">{log.details || log.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add/Edit Candidate Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {currentCandidate ? 'Edit Candidate' : 'Add Candidate'}
            </h2>
            <CandidateForm
              candidate={currentCandidate}
              onSave={handleSave}
              onCancel={closeModal}
            />
          </div>
        </div>
      )}

      {/* View Details Modal */}
      {isDetailsModalOpen && currentCandidate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Candidate Details</h2>
            <p className="mb-2">
              <strong>Name:</strong> {currentCandidate.name}
            </p>
            <p className="mb-2">
              <strong>Email:</strong> {currentCandidate.email}
            </p>
            <p className="mb-2">
              <strong>Domain:</strong> {currentCandidate.domain}
            </p>
            <p className="mb-2">
              <strong>Status:</strong> {currentCandidate.status}
            </p>
            <div className="mb-4">
              <label className="block text-gray-700 font-semibold mb-2">Interview Answers</label>
              <input
                type="text"
                value={editedAnswers}
                onChange={e => setEditedAnswers(e.target.value)}
                className="w-full border-2 border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={handleSaveAnswers}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
              >
                Save Answers
              </button>
              <button
                onClick={closeDetailsModal}
                className="bg-gray-300 text-black px-4 py-2 rounded-lg hover:bg-gray-400 transition duration-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const CandidateForm = ({ candidate, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: candidate ? candidate.name : '',
    email: candidate ? candidate.email : '',
    domain: candidate ? candidate.domain : '',
    status: candidate ? candidate.status : 'New',
    interview_answers: candidate ? candidate.interview_answers?.join(', ') : '',
  });

  const handleChange = e => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onSave(formData);
  };

  return (
    <div>
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Name</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="w-full border-2 border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Email</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="w-full border-2 border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Domain</label>
        <select
          name="domain"
          value={formData.domain}
          onChange={handleChange}
          className="w-full border-2 border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        >
          <option value="">Select Domain</option>
          <option value="React">React</option>
          <option value="Python">Python</option>
          <option value="Node.js">Node.js</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Status</label>
        <select
          name="status"
          value={formData.status}
          onChange={handleChange}
          className="w-full border-2 border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        >
          <option value="New">New</option>
          <option value="Shortlisted">Shortlisted</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">Interview Answers</label>
        <input
          type="text"
          name="interview_answers"
          value={formData.interview_answers}
          onChange={handleChange}
          className="w-full border-2 border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter answers separated by commas"
        />
      </div>
      <div className="flex justify-end space-x-2">
        <button
          onClick={onCancel}
          className="bg-gray-300 text-black px-4 py-2 rounded-lg hover:bg-gray-400 transition duration-200"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
        >
          Save
        </button>
      </div>
    </div>
  );
};

export default AdminDashboard;
