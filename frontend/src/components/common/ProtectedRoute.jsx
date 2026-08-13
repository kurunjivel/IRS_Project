import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ProtectedRoute = ({ children, allowedRole }) => {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRole && user?.role !== allowedRole) {
    if (user?.role === 'HR') {
      return <Navigate to="/hr" replace />;
    } else if (user?.role === 'EMPLOYEE') {
      return <Navigate to="/employee" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
