import React, { useState, useEffect } from 'react';
import { getMyRoadmap } from '../api/employeePortalApi';
import { Map, Calendar, CheckCircle2, Clock } from 'lucide-react';

export const EmployeeRoadmapView = () => {
  const [roadmap, setRoadmap] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyRoadmap()
      .then(res => setRoadmap(res.timeline || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading career roadmap...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Career Progression Roadmap</h1>
        <p className="text-xs text-slate-400">Step-by-step milestone timeline to qualify for your target promotion</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <div className="relative border-l-2 border-indigo-500/30 ml-4 space-y-8 pl-6">
          {roadmap.map((item, idx) => (
            <div key={idx} className="relative">
              <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-indigo-500 border-4 border-slate-900 shadow-md shadow-indigo-500/50" />
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl">
                <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">{item.quarter || `Phase ${idx + 1}`}</span>
                <h3 className="text-xs font-bold text-slate-200 mt-1">{item.title || item.action}</h3>
                <p className="text-xs text-slate-400 mt-1">{item.description || item.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EmployeeRoadmapView;
