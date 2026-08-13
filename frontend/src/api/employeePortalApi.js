import api from './axios';

export const getMyProfile = () => api.get('/employee/me');
export const getMyCareerAnalysis = () => api.get('/employee/me/career-analysis');
export const getMyReadiness = () => api.get('/employee/me/readiness');
export const getMyRecommendations = () => api.get('/employee/me/recommendations');
export const getMyGapAnalysis = () => api.get('/employee/me/gap-analysis');
export const getMyRoadmap = () => api.get('/employee/me/roadmap');
export const getMyProgress = () => api.get('/employee/me/progress');
export const getMyPromotionStatus = () => api.get('/employee/me/promotion-status');
