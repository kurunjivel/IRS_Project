import api from './axios';

export const getHREmployees = () => api.get('/hr/employees');
export const getHRRoles = () => api.get('/hr/roles');
export const getRoleCandidates = (roleId) => api.get(`/hr/roles/${roleId}/candidates`);
export const getHREmployeeCareerAnalysis = (empId) => api.get(`/hr/employees/${empId}/career-analysis`);
export const getHREmployeePromotionStatus = (empId) => api.get(`/hr/employees/${empId}/promotion-status`);
export const getHRAnalytics = () => api.get('/hr/analytics');
