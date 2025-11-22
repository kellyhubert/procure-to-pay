import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { requestsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './RequestList.css';

const RequestList = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadRequests();
  }, [filter]);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await requestsAPI.list(params);
      setRequests(response.data.results || response.data);
      setError('');
    } catch (err) {
      setError('Failed to load requests');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { class: 'status-pending', label: 'Pending' },
      approved: { class: 'status-approved', label: 'Approved' },
      rejected: { class: 'status-rejected', label: 'Rejected' },
    };
    return badges[status] || { class: '', label: status };
  };

  if (loading) {
    return <div className="loading">Loading requests...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="request-list">
      <div className="list-header">
        <h3>Purchase Requests</h3>
        <div className="filter-tabs">
          <button
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={filter === 'pending' ? 'active' : ''}
            onClick={() => setFilter('pending')}
          >
            Pending
          </button>
          <button
            className={filter === 'approved' ? 'active' : ''}
            onClick={() => setFilter('approved')}
          >
            Approved
          </button>
          <button
            className={filter === 'rejected' ? 'active' : ''}
            onClick={() => setFilter('rejected')}
          >
            Rejected
          </button>
        </div>
      </div>

      {requests.length === 0 ? (
        <div className="no-requests">
          <p>No requests found</p>
          {user?.role === 'staff' && (
            <button
              onClick={() => navigate('/requests/new')}
              className="btn-primary"
            >
              Create Your First Request
            </button>
          )}
        </div>
      ) : (
        <div className="requests-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Created By</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request) => {
                const badge = getStatusBadge(request.status);
                return (
                  <tr key={request.id}>
                    <td>#{request.id}</td>
                    <td>{request.title}</td>
                    <td>${parseFloat(request.amount).toFixed(2)}</td>
                    <td>
                      <span className={`status-badge ${badge.class}`}>
                        {badge.label}
                      </span>
                    </td>
                    <td>{request.created_by?.username || 'Unknown'}</td>
                    <td>{new Date(request.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        onClick={() => navigate(`/requests/${request.id}`)}
                        className="btn-view"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default RequestList;
