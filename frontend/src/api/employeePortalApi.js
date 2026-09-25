import api from './axios';

export const getMyProfile = () => api.get('/employee/me');
export const getMyCareerAnalysis = () => api.get('/employee/me/career-analysis');
export const getMyReadiness = () => api.get('/employee/me/readiness');
export const getMyRecommendations = () => api.get('/employee/me/recommendations');
export const getMyGapAnalysis = () => api.get('/employee/me/gap-analysis');
export const getMyRoadmap = () => api.get('/employee/me/roadmap');
export const getMyProgress = () => api.get('/employee/me/progress');
export const getMyPromotionStatus = () => api.get('/employee/me/promotion-status');
export const getMyMentors = () => api.get('/employee/me/mentors');
export const getMyAttritionRisk = () => api.get('/employee/me/attrition-risk');
export const requestMentorship = (payload) => api.post('/mentors/request', payload);
export const simulateWhatIf = (payload) => api.post('/simulation/what-if', payload);
