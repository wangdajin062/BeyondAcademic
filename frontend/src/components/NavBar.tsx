import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export const NavBar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem('access_token');
  const isLoggedIn = !!token;

  // Hide navbar on login page for a clean auth screen
  if (location.pathname === '/login') return null;

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">BeyondAcademic</Link>
      </div>
      {isLoggedIn && (
        <>
          <div className="navbar-links">
            <Link to="/articles" className={isActive('/articles') ? 'active' : ''}>
              Articles
            </Link>
            <Link to="/workflows" className={isActive('/workflows') ? 'active' : ''}>
              Workflows
            </Link>
            <Link to="/literature" className={isActive('/literature') ? 'active' : ''}>
              Literature
            </Link>
          </div>
          <div className="navbar-user">
            <span className="navbar-user-name">Researcher</span>
            <button className="navbar-logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </>
      )}
    </nav>
  );
};
