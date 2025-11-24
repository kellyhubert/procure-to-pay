import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Procure-to-Pay System</h1>
        <h2>Login</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* <div className="divider">
          <span>Demo Account</span>
        </div> */}

        <div className="demo-accounts">
          <div className="demo-info">
            <p className="demo-title">🔑 Quick Access</p>
            <div className="demo-credential">
              <span className="label">Username:</span>
              <code>admin</code>
            </div>
            <div className="demo-credential">
              <span className="label">Password:</span>
              <code>admin123</code>
            </div>
            <p className="demo-hint">
              💡 <strong>Tip:</strong> Use Django Admin Panel to create users with different roles:
              <br/>Staff, Approver L1, Approver L2, or Finance
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
