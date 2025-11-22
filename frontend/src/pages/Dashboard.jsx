import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import RequestList from '../components/RequestList';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getRoleDisplay = (role) => {
    const roleMap = {
      'staff': 'Staff',
      'approver-level-1': 'Approver Level 1',
      'approver-level-2': 'Approver Level 2',
      'finance': 'Finance'
    };
    return roleMap[role] || role;
  };

  if (!user) return null;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Procure-to-Pay System</h1>
          <div className="user-info">
            <span className="user-name">{user.username}</span>
            <span className="user-role">{getRoleDisplay(user.role)}</span>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="welcome-section">
            <h2>Welcome, {user.first_name || user.username}!</h2>
            <p className="role-description">
              {user.role === 'staff' && 'You can create and manage purchase requests.'}
              {user.role === 'approver-level-1' && 'You can review and approve Level 1 requests.'}
              {user.role === 'approver-level-2' && 'You can review and approve Level 2 requests.'}
              {user.role === 'finance' && 'You have full access to all requests and data.'}
            </p>
          </div>

          {user.role === 'staff' && (
            <div className="action-buttons">
              <button
                onClick={() => navigate('/requests/new')}
                className="btn-primary btn-large"
              >
                + Create New Request
              </button>
            </div>
          )}

          <RequestList />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
