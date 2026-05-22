import React, { useState } from 'react';
import { authAPI } from '../services/authAPI';
import { LoginResponse } from '../types/auth';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('tester');
  const [password, setPassword] = useState('test123456');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<LoginResponse | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const loginResult = await authAPI.testLogin({ username, password });
      setResult(loginResult);
      localStorage.setItem('access_token', loginResult.access_token);
      window.location.href = '/articles';
    } catch {
      setResult(null);
      setError('Login failed. Use tester/test123456 or researcher/Research@2026');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">BeyondAcademic</h1>
        <p className="login-subtitle">Academic Paper Writing Platform</p>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input className="form-input" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button type="submit" disabled={loading} className="btn btn-primary btn-block">
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        {error && <p className="login-error">{error}</p>}

        {result && (
          <div className="login-success">
            <h3>Login Success</h3>
            <p><strong>User:</strong> {result.user.display_name} ({result.user.username})</p>
            <p><strong>Role:</strong> {result.user.role}</p>
            <p><strong>Token expires:</strong> {new Date(result.expires_at).toLocaleString()}</p>
            <code className="login-token">{result.access_token}</code>
            <div className="login-success-actions">
              <a href="/articles" className="btn btn-primary btn-sm">Go to Articles</a>
              <a href="/workflows" className="btn btn-secondary btn-sm">Go to Workflows</a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
