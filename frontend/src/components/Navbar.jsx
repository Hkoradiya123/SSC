import React, { useState } from 'react';
import styles from './navbar.module.css';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { authService } from '../utils/api';

export function Navbar({ isAuthenticated, user }) {
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const navClassName = ({ isActive }) =>
    `${styles.navLink} ${isActive ? styles.active : ''}`.trim();

  const handleLogout = async () => {
    if (isLoggingOut) return;

    try {
      setIsLoggingOut(true);
      authService.logout();
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      sessionStorage.setItem('suppressSocialAutoLogin', '1');
      window.location.replace('/login');
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          🏏 SSC
        </Link>

        <div className={styles.navlinks}>
          {isAuthenticated ? (
            <>
              <NavLink to="/dashboard" className={navClassName}>Dashboard</NavLink>
              <NavLink to="/players" className={navClassName}>Players</NavLink>
              <NavLink to="/matches" className={navClassName}>Matches</NavLink>
              <NavLink to="/profile" className={navClassName}>Profile</NavLink>
              <NavLink to="/finance" className={navClassName}>Finance</NavLink>
              {user?.role === 'admin' && (
                <NavLink to="/admin" className={navClassName}>Admin</NavLink>
              )}
              <button onClick={handleLogout} className={styles.logout} disabled={isLoggingOut}>
                {isLoggingOut ? 'Logging out...' : 'Logout'}
              </button>
            </>
          ) : (
            <>
              <NavLink to="/" end className={navClassName}>Home</NavLink>
              <NavLink to="/login" className={navClassName}>Login</NavLink>
              <NavLink to="/register" className={({ isActive }) => `${styles.register} ${isActive ? styles.activeRegister : ''}`.trim()}>
                Register
              </NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
