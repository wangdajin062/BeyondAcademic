import React, { useState } from 'react';
import { authAPI } from '../services/authAPI';
import { LoginResponse } from '../types/auth';

interface LoginPageProps {
  onLoginSuccess?: (result: LoginResponse) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('tester');
  const [password, setPassword] = useState('test123456');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await authAPI.testLogin({ username, password });
      if (onLoginSuccess) {
        onLoginSuccess(result);
      }
    } catch {
      setError('Login failed. Use tester/test123456 or researcher/Research@2026');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{
      maxWidth: 440, margin: '80px auto', padding: '32px',
      fontFamily: 'Arial, sans-serif', boxShadow: '0 2px 16px rgba(0,0,0,0.1)',
      borderRadius: '8px'
    }}>
      <h1 style={{ marginBottom: '4px' }}>BeyondAcademic</h1>
      <p style={{ color: '#666', marginBottom: '24px' }}>AI-Powered Academic Writing System</p>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '14px' }}>
        <label style={{ display: 'grid', gap: '4px' }}>
          <span>Username</span>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
            autoComplete="username"
          />
        </label>
        <label style={{ display: 'grid', gap: '4px' }}>
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
            autoComplete="current-password"
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '10px', background: '#1a2f5a', color: '#fff',
            border: 'none', borderRadius: '4px', cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '1rem'
          }}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>

      {error && (
        <p style={{ color: '#b00020', marginTop: '12px', fontSize: '0.9rem' }}>{error}</p>
      )}

      <p style={{ marginTop: '20px', fontSize: '0.8rem', color: '#999' }}>
        Demo accounts: <code>tester / test123456</code> or <code>researcher / Research@2026</code>
      </p>
    </main>
  );
};
