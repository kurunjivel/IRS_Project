import React, { useState, useEffect } from 'react';
import { getMyProgress } from '../api/employeePortalApi';
import { TrendingUp, Target, Award, CheckCircle } from 'lucide-react';

export const EmployeeProgressView = () => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyProgress()
      .then(res => setProgress(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading progress...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Career Progression Tracking</h1>
        <p className="text-xs text-slate-400">Real-time evaluation of your promotion readiness</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-5 bg-slate-950 border border-slate-800 rounded-2xl">
            <p className="text-xs font-bold text-slate-400 uppercase">Readiness Score</p>
            <p className="text-3xl font-extrabold text-indigo-400 mt-2">{progress?.readiness_score?.toFixed(1)} / 100</p>
          </div>
          <div className="p-5 bg-slate-950 border border-slate-800 rounded-2xl">
            <p className="text-xs font-bold text-slate-400 uppercase">Promotion Probability</p>
            <p className="text-3xl font-extrabold text-purple-400 mt-2">{((progress?.promotion_probability || 0) * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeProgressView;
