import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

export const ReadinessBreakdownChart = ({ breakdown }) => {
  if (!breakdown) return null;

  // Transform breakdown dict into chart data array
  const categoryNames = {
    skills: 'Skills (40%)',
    certifications: 'Certifications (15%)',
    experience: 'Experience (15%)',
    projects: 'Projects (20%)',
    performance: 'Performance (10%)',
  };

  const colors = {
    skills: '#6366f1',
    certifications: '#06b6d4',
    experience: '#10b981',
    projects: '#f59e0b',
    performance: '#ec4899',
  };

  const chartData = Object.entries(breakdown).map(([key, item]) => {
    const score = item.score ?? 0;
    const maxScore = item.max_score ?? (key === 'skills' ? 40 : key === 'certifications' ? 15 : key === 'experience' ? 15 : key === 'projects' ? 20 : 10);
    const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0;

    return {
      category: categoryNames[key] || key,
      score: Number(score.toFixed(2)),
      maxScore,
      percentage: Number(percentage.toFixed(1)),
      color: colors[key] || '#6366f1',
      weight: `${(item.weight * 100).toFixed(0)}%`,
    };
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 shadow-2xl text-xs space-y-1">
          <p className="font-bold text-slate-100">{d.category}</p>
          <p className="text-indigo-400">Score: <strong className="text-white">{d.score} / {d.maxScore}</strong></p>
          <p className="text-emerald-400">Fulfillment: <strong className="text-white">{d.percentage}%</strong></p>
          <p className="text-slate-400">Weightage: {d.weight}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Readiness Breakdown Chart</h3>
          <p className="text-xs text-slate-400">Weighted scores across 5 core evaluation dimensions</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={chartData}
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} stroke="#64748b" tickFormatter={(v) => `${v}%`} />
            <YAxis type="category" dataKey="category" stroke="#94a3b8" tick={{ fontSize: 12 }} width={120} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="percentage" radius={[0, 8, 8, 0]} barSize={20}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ReadinessBreakdownChart;
