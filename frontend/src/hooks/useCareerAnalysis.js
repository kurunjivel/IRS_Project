import { useState, useEffect } from 'react';
import { getCareerAnalysis } from '../api/careerApi';

export const useCareerAnalysis = (employeeId = 1) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getCareerAnalysis(employeeId);
      setData(res);
    } catch (err) {
      console.error(`Error loading career analysis for employee ${employeeId}:`, err);
      setError(
        err.response?.data?.detail ||
        'Unable to load career analysis. Please check that the IRS FastAPI backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (employeeId) {
      fetchAnalysis();
    }
  }, [employeeId]);

  return { data, loading, error, refetch: fetchAnalysis };
};
