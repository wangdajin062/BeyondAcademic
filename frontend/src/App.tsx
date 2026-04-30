import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useParams } from 'react-router-dom';
import { LoginPage } from './components/LoginPage';
import { ArticleList } from './components/ArticleList';
import { AcademicEditor } from './components/AcademicEditor';
import { LoginResponse } from './types/auth';

// Simple auth context via localStorage
function getStoredAuth(): LoginResponse | null {
  try {
    const raw = localStorage.getItem('ba_auth');
    if (!raw) return null;
    const parsed: LoginResponse = JSON.parse(raw);
    if (new Date(parsed.expires_at) < new Date()) {
      localStorage.removeItem('ba_auth');
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const auth = getStoredAuth();
  if (!auth) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function LoginRoute() {
  const navigate = useNavigate();

  const handleLoginSuccess = (result: LoginResponse) => {
    localStorage.setItem('ba_auth', JSON.stringify(result));
    navigate('/articles');
  };

  return <LoginPage onLoginSuccess={handleLoginSuccess} />;
}

function EditorRoute() {
  const { articleId } = useParams<{ articleId: string }>();
  const [content, setContent] = useState('');

  return (
    <div style={{ padding: '16px' }}>
      <a href="/articles" style={{ marginBottom: '16px', display: 'inline-block' }}>
        &larr; Back to Articles
      </a>
      <AcademicEditor
        content={content}
        template="Generic"
        onChange={setContent}
      />
    </div>
  );
}

function NavBar() {
  const auth = getStoredAuth();

  const handleLogout = () => {
    localStorage.removeItem('ba_auth');
    window.location.href = '/login';
  };

  if (!auth) return null;
  return (
    <nav style={{
      background: '#1a2f5a', color: '#fff', padding: '12px 24px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between'
    }}>
      <a href="/articles" style={{ color: '#fff', fontWeight: 700, textDecoration: 'none', fontSize: '1.1rem' }}>
        BeyondAcademic
      </a>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ fontSize: '0.9rem' }}>
          {auth.user.display_name} &middot; {auth.user.role}
        </span>
        <button
          onClick={handleLogout}
          style={{
            background: 'transparent', border: '1px solid #fff',
            color: '#fff', padding: '4px 12px', cursor: 'pointer', borderRadius: '4px'
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

const App: React.FC = () => (
  <BrowserRouter>
    <NavBar />
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route
        path="/articles"
        element={
          <RequireAuth>
            <ArticleList />
          </RequireAuth>
        }
      />
      <Route
        path="/editor/:articleId"
        element={
          <RequireAuth>
            <EditorRoute />
          </RequireAuth>
        }
      />
      <Route path="/" element={<Navigate to="/articles" replace />} />
      <Route path="*" element={<Navigate to="/articles" replace />} />
    </Routes>
  </BrowserRouter>
);

export default App;
