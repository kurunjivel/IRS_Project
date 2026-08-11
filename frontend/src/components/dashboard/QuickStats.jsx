import React from 'react';
import { Lightbulb, Flame, Calendar, CheckSquare } from 'lucide-react';

export const QuickStats = ({ recommendations }) => {
  if (!recommendations) return null;

  const summary = recommendations.summary || { total: 0, high: 0, medium: 0, low: 0 };
  const urgency = recommendations.urgency || 'Normal';

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {/* Total Recommendations */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-3">
        <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
          <Lightbulb className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Recommendations</p>
          <p className="text-xl font-bold text-slate-100">{summary.total}</p>
        </div>
      </div>

      {/* High Priority Actions */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-3">
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl">
          <Flame className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">High Priority</p>
          <p className="text-xl font-bold text-slate-100">{summary.high}</p>
        </div>
      </div>

      {/* Engine Urgency */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-3">
        <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl">
          <CheckSquare className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Urgency Level</p>
          <p className="text-xl font-bold text-slate-100">{urgency}</p>
        </div>
      </div>

      {/* Timeline Milestones */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-3">
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl">
          <Calendar className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Milestones</p>
          <p className="text-xl font-bold text-slate-100">{recommendations.timeline?.length || 0}</p>
        </div>
      </div>
    </div>
  );
};

export default QuickStats;
