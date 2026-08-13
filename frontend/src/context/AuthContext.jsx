import React, { createContext, useState, useEffect, useContext } from 'react';
import * as authApi from '../api/authApi';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('irs_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await authApi.login(username, password);

      const userPayload = {
        user_id: res.user_id,
        username: res.username,
        role: res.role,
        employee_id: res.employee_id,
      };
      localStorage.setItem('irs_token', res.access_token);
      localStorage.setItem('irs_user', JSON.stringify(userPayload));
      setUser(userPayload);
      setLoading(false);
      return userPayload;
    } catch (err) {
      setLoading(false);
      const msg = err.response?.data?.detail || 'Invalid login credentials';
      setError(msg);
      throw new Error(msg);
    }
  };

  const handleRegister = async (username, password, role = 'EMPLOYEE', employeeId = null) => {
    setLoading(true);
    setError(null);
    try {
      const res = await authApi.register(username, password, role, employeeId);

      const userPayload = {
        user_id: res.user_id,
        username: res.username,
        role: res.role,
        employee_id: res.employee_id,
      };
      localStorage.setItem('irs_token', res.access_token);
      localStorage.setItem('irs_user', JSON.stringify(userPayload));
      setUser(userPayload);
      setLoading(false);
      return userPayload;
    } catch (err) {
      setLoading(false);
      const msg = err.response?.data?.detail || 'Registration failed';
      setError(msg);
      throw new Error(msg);
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      console.warn('Logout notification error:', e);
    } finally {
      localStorage.removeItem('irs_token');
      localStorage.removeItem('irs_user');
      setUser(null);
    }
  };

  const value = {
    user,
    loading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    isAuthenticated: !!user,
    isHR: user?.role === 'HR',
    isEmployee: user?.role === 'EMPLOYEE',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
