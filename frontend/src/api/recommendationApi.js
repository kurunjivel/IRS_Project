import api from './axios';

export const getRecommendations = (id) => {
  return api.get(`/recommendations/${id}`);
};
