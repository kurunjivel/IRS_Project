import axios from 'axios';

const API_BASE_URL = '/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const managerPortalApi = {
  getManagerTeam: async () => {
    const response = await axios.get(`${API_BASE_URL}/manager/team`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  getEmployeeDossier: async (employeeId) => {
    const response = await axios.get(`${API_BASE_URL}/manager/employee/${employeeId}`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  submitManagerReview: async (payload) => {
    const response = await axios.post(`${API_BASE_URL}/manager/review`, payload, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  getEmployeeAuditHistory: async (employeeId) => {
    const response = await axios.get(`${API_BASE_URL}/manager/employee/${employeeId}/audit-history`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },
};
