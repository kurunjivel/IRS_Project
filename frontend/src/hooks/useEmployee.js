import { useState, useEffect } from 'react';
import { getEmployee } from '../api/employeeApi';

export const useEmployee = (employeeId = 1) => {
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    getEmployee(employeeId)
      .then((data) => {
        if (isMounted) {
          setEmployee(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load employee profile.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [employeeId]);

  return { employee, loading, error };
};
