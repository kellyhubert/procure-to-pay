import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { requestsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './RequestDetail.css';

const RequestDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [comments, setComments] = useState('');
  const [receiptFile, setReceiptFile] = useState(null);

  useEffect(() => {
    loadRequest();
  }, [id]);

  const loadRequest = async () => {
    try {
      setLoading(true);
      const response = await requestsAPI.get(id);
      setRequest(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load request details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!window.confirm('Are you sure you want to approve this request?')) return;

    setActionLoading(true);
    try {
      await requestsAPI.approve(id, comments);
      await loadRequest();
      setComments('');
      alert('Request approved successfully');
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to approve request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!comments.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    if (!window.confirm('Are you sure you want to reject this request?')) return;

    setActionLoading(true);
    try {
      await requestsAPI.reject(id, comments);
      await loadRequest();
      setComments('');
      alert('Request rejected');
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to reject request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReceiptSubmit = async () => {
    if (!receiptFile) {
      alert('Please select a receipt file');
      return;
    }

    setActionLoading(true);
    try {
      await requestsAPI.submitReceipt(id, receiptFile);
      await loadRequest();
      setReceiptFile(null);
      alert('Receipt uploaded successfully');
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to upload receipt');
    } finally {
      setActionLoading(false);
    }
  };

  const canApprove = () => {
    if (!user || !request) return false;
    const isApprover = user.role === 'approver-level-1' || user.role === 'approver-level-2';
    const isPending = request.status === 'pending';
    const hasNotApproved = !request.approvals?.some(a => a.approver.id === user.id);
    return isApprover && isPending && hasNotApproved;
  };

  const canSubmitReceipt = () => {
    if (!user || !request) return false;
    return user.id === request.created_by?.id && request.status === 'approved' && !request.receipt;
  };

  if (loading) {
    return <div className="loading">Loading request details...</div>;
  }

  if (error || !request) {
    return (
      <div className="error-container">
        <p className="error-message">{error || 'Request not found'}</p>
        <button onClick={() => navigate('/dashboard')} className="btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const getStatusClass = (status) => {
    const classes = {
      pending: 'status-pending',
      approved: 'status-approved',
      rejected: 'status-rejected',
    };
    return classes[status] || '';
  };

  return (
    <div className="request-detail-container">
      <div className="detail-header">
        <button onClick={() => navigate('/dashboard')} className="btn-back">
          ← Back to Dashboard
        </button>
        <div className="header-title">
          <h1>Request #{request.id}</h1>
          <span className={`status-badge ${getStatusClass(request.status)}`}>
            {request.status.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="detail-content">
        <section className="detail-section">
          <h2>Request Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Title:</label>
              <span>{request.title}</span>
            </div>
            <div className="info-item">
              <label>Amount:</label>
              <span>${parseFloat(request.amount).toFixed(2)}</span>
            </div>
            <div className="info-item">
              <label>Created By:</label>
              <span>{request.created_by?.username || 'Unknown'}</span>
            </div>
            <div className="info-item">
              <label>Created At:</label>
              <span>{new Date(request.created_at).toLocaleString()}</span>
            </div>
            <div className="info-item full-width">
              <label>Description:</label>
              <p>{request.description}</p>
            </div>
          </div>
        </section>

        {request.proforma && (
          <section className="detail-section">
            <h2>Proforma Invoice</h2>
            <a href={request.proforma} target="_blank" rel="noopener noreferrer" className="file-link">
              View Proforma Document
            </a>
            {request.proforma_data && (
              <div className="extracted-data">
                <h3>Extracted Data (AI-Powered)</h3>
                <pre>{JSON.stringify(request.proforma_data, null, 2)}</pre>
              </div>
            )}
          </section>
        )}

        {request.approvals && request.approvals.length > 0 && (
          <section className="detail-section">
            <h2>Approval History</h2>
            <div className="approvals-list">
              {request.approvals.map((approval, index) => (
                <div key={index} className="approval-item">
                  <div className="approval-header">
                    <strong>{approval.approver.username}</strong>
                    <span className={approval.approved ? 'approved' : 'rejected'}>
                      {approval.approved ? '✓ Approved' : '✗ Rejected'}
                    </span>
                  </div>
                  {approval.comments && <p className="approval-comments">{approval.comments}</p>}
                  <small>{new Date(approval.approved_at).toLocaleString()}</small>
                </div>
              ))}
            </div>
          </section>
        )}

        {request.purchase_order && (
          <section className="detail-section">
            <h2>Purchase Order</h2>
            <a href={request.purchase_order} target="_blank" rel="noopener noreferrer" className="file-link">
              View Purchase Order
            </a>
          </section>
        )}

        {request.receipt && (
          <section className="detail-section">
            <h2>Receipt</h2>
            <a href={request.receipt} target="_blank" rel="noopener noreferrer" className="file-link">
              View Receipt
            </a>
            {request.receipt_validation && (
              <div className="validation-result">
                <h3>Validation Results</h3>
                <div className={`validation-status ${request.receipt_validation.status}`}>
                  <strong>Status:</strong> {request.receipt_validation.status}
                </div>
                {request.receipt_validation.discrepancies && request.receipt_validation.discrepancies.length > 0 && (
                  <div className="discrepancies">
                    <h4>Discrepancies Found:</h4>
                    <ul>
                      {request.receipt_validation.discrepancies.map((disc, idx) => (
                        <li key={idx}>{disc.message}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {canApprove() && (
          <section className="detail-section action-section">
            <h2>Approve or Reject</h2>
            <div className="form-group">
              <label htmlFor="comments">Comments (required for rejection):</label>
              <textarea
                id="comments"
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows="3"
                placeholder="Add your comments here..."
                disabled={actionLoading}
              />
            </div>
            <div className="action-buttons">
              <button
                onClick={handleApprove}
                className="btn-approve"
                disabled={actionLoading}
              >
                ✓ Approve
              </button>
              <button
                onClick={handleReject}
                className="btn-reject"
                disabled={actionLoading}
              >
                ✗ Reject
              </button>
            </div>
          </section>
        )}

        {canSubmitReceipt() && (
          <section className="detail-section action-section">
            <h2>Submit Receipt</h2>
            <div className="form-group">
              <label htmlFor="receipt">Upload Receipt:</label>
              <input
                id="receipt"
                type="file"
                onChange={(e) => setReceiptFile(e.target.files[0])}
                accept=".pdf,.jpg,.jpeg,.png"
                disabled={actionLoading}
              />
            </div>
            <button
              onClick={handleReceiptSubmit}
              className="btn-primary"
              disabled={actionLoading}
            >
              Upload Receipt
            </button>
          </section>
        )}
      </div>
    </div>
  );
};

export default RequestDetail;
