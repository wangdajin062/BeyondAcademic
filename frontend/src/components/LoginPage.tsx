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
    } catch {
      setResult(null);
      setError('Login failed. Use tester/test123456 or researcher/Research@2026');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 520, margin: '48px auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>BeyondAcademic Test Login</h1>
      <p>Use this page to verify authentication wiring in development and deployment.</p>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12 }}>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: '100%', padding: 8 }} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: '100%', padding: 8 }} />
        </label>
        <button type="submit" disabled={loading} style={{ padding: 10 }}>
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>

      {error && <p style={{ color: '#b00020', marginTop: 16 }}>{error}</p>}

      {result && (
        <section style={{ marginTop: 20, padding: 12, background: '#f4f7ff', borderRadius: 8 }}>
          <h2>Login Success</h2>
          <p><strong>User:</strong> {result.user.display_name} ({result.user.username})</p>
          <p><strong>Role:</strong> {result.user.role}</p>
          <p><strong>Token expires:</strong> {new Date(result.expires_at).toLocaleString()}</p>
          <code style={{ display: 'block', overflowWrap: 'anywhere' }}>{result.access_token}</code>
        </section>
      )}
    </main>
  );
};
