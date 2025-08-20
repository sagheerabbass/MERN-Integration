import React, { useState, useEffect, useCallback } from 'react';
import { candidateAPI, logAPI } from '../services/api';

const CandidateDashboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    page: 1,
    limit: 10
  });

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const [candidatesRes, statsRes, logsRes] = await Promise.all([
        candidateAPI.getAll(filters),
        candidateAPI.getStats(),
        logAPI.getAll({ limit: 10 })
      ]);

      // Services return the response data (not the full axios response).
      // Adjust to the expected shapes returned by the API service.
      setCandidates((candidatesRes && candidatesRes.candidates) || []);
      setStats(statsRes || {});
      setLogs((logsRes && logsRes.logs) || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const handleStatusUpdate = async (id, newStatus) => {
    try {
      await candidateAPI.updateStatus(id, newStatus);
      loadDashboardData(); // Refresh all data
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="candidate-dashboard">
      <h1>AI Intern Candidate Dashboard</h1>
      
      {/* Statistics Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Candidates</h3>
            <p>{stats.total}</p>
          </div>
          <div className="stat-card">
            <h3>Shortlisted</h3>
            <p>{stats.shortlisted}</p>
          </div>
          <div className="stat-card">
            <h3>Pending</h3>
            <p>{stats.pending}</p>
          </div>
          <div className="stat-card">
            <h3>Rejected</h3>
            <p>{stats.rejected}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search by name, email, or position..."
          value={filters.search}
          onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value, page: 1 }))}
        />
        <select
          value={filters.status}
          onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value, page: 1 }))}
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="rejected">Rejected</option>
          <option value="interviewed">Interviewed</option>
          <option value="hired">Hired</option>
        </select>
      </div>

      {/* Candidates Table */}
      <div className="candidates-section">
        <h2>Candidates</h2>
        <table className="candidates-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Position</th>
              <th>Experience</th>
              <th>Score</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map(candidate => (
              <tr key={candidate._id}>
                <td>{candidate.name}</td>
                <td>{candidate.email}</td>
                <td>{candidate.appliedPosition}</td>
                <td>{candidate.experience} years</td>
                <td>{candidate.score}</td>
                <td>
                  <span className={`status ${candidate.status}`}>{candidate.status}</span>
                </td>
                <td>
                  <select
                    value={candidate.status}
                    onChange={(e) => handleStatusUpdate(candidate._id, e.target.value)}
                  >
                    <option value="pending">Pending</option>
                    <option value="shortlisted">Shortlisted</option>
                    <option value="rejected">Rejected</option>
                    <option value="interviewed">Interviewed</option>
                    <option value="hired">Hired</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Recent Activity */}
      <div className="activity-section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          {logs.map(log => (
            <div key={log._id} className="activity-item">
              <p>{log.action}</p>
              <small>{new Date(log.createdAt).toLocaleString()}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CandidateDashboard;

