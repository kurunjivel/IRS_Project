import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export const SkillGapChart = ({ skills = [] }) => {
  if (!skills || skills.length === 0) return null;

  const data = skills.map((s) => ({
    name: s.skill,
    current: s.current_level,
    required: s.required_level,
    gap: s.gap,
  }));

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Skill Gap Proficiency Comparison</h3>
        <p className="text-xs text-slate-400">Current employee proficiency level vs target grade requirement</p>
      </div>

      <div className="h-60 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" domain={[0, 5]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
              itemStyle={{ color: '#f8fafc' }}
            />
            <Legend wrapperStyle={{ paddingTop: '10px' }} />
            <Bar dataKey="current" name="Current Level" fill="#6366f1" radius={[4, 4, 0, 0]} />
            <Bar dataKey="required" name="Required Level" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default SkillGapChart;
