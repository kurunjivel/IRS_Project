import React, { useState, useEffect } from 'react';
import { getHRAnalytics } from '../api/hrApi';
import { BarChart3, Users, Target, Award } from 'lucide-react';

export const HRAnalyticsView = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHRAnalytics()
      .then(res => setAnalytics(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading talent analytics...</div>;
  }

  const gradeDist = analytics?.grade_distribution || {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Workforce Talent Analytics</h1>
        <p className="text-xs text-slate-400">Distribution and metrics across organizational grades</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-purple-400" />
          Grade Distribution Breakdown
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {Object.entries(gradeDist).map(([grade, count]) => (
            <div key={grade} className="p-4 bg-slate-950 border border-slate-800 rounded-2xl text-center">
              <p className="text-xs font-bold text-slate-400 uppercase">Grade {grade}</p>
              <p className="text-2xl font-extrabold text-purple-400 mt-1">{count} Employees</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HRAnalyticsView;
