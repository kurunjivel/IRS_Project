import api from './axios';

export const login = (username, password) => {
  return api.post('/auth/login', { username, password });
};

export const register = (username, password, role = 'EMPLOYEE', employeeId = null) => {
  return api.post('/auth/register', { username, password, role, employee_id: employeeId });
};

export const logout = () => {
  return api.post('/auth/logout');
};

export const getMe = () => {
  return api.get('/auth/me');
};
