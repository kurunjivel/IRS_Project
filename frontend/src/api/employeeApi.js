import api from './axios';

export const getEmployee = (id) => {
  return api.get(`/employee/${id}`);
};
