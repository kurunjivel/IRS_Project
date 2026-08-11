import api from './axios';

export const getCareerAnalysis = (id) => {
  return api.get(`/career-analysis/${id}`);
};

export const getGapAnalysis = (id) => {
  return api.get(`/gap-analysis/${id}`);
};

export const getReadiness = (id) => {
  return api.get(`/readiness/${id}`);
};

export const getPrediction = (id) => {
  return api.get(`/prediction/${id}`);
};
