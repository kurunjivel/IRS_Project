import { useState, useEffect } from 'react';
import { getRecommendations } from '../api/recommendationApi';

export const useRecommendations = (employeeId = 1) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    getRecommendations(employeeId)
      .then((data) => {
        if (isMounted) {
          setRecommendations(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load recommendations.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [employeeId]);

  return { recommendations, loading, error };
};
