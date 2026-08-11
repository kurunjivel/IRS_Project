import React from 'react';
import { Briefcase, CheckCircle2 } from 'lucide-react';
import ProgressBar from '../common/ProgressBar';

export const ProjectGapCard = ({ projects }) => {
  if (!projects) return null;

  const total = projects.total_projects ?? 0;
  const required = projects.required_projects ?? 0;
  const remaining = projects.remaining_projects ?? 0;

  const leadDone = projects.lead_projects ?? 0;
  const leadRequired = projects.required_lead_projects ?? 0;
  const leadRemaining = projects.remaining_lead_projects ?? 0;

  const totalSatisfied = remaining <= 0;
  const leadSatisfied = leadRemaining <= 0;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-xl">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-base font-bold text-slate-100">Project Portfolio Requirement</h4>
            <p className="text-xs text-slate-400">Total completed projects & leadership role assignments</p>
          </div>
        </div>

        {totalSatisfied && leadSatisfied ? (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl text-xs font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Satisfied</span>
          </span>
        ) : (
          <span className="px-3 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-xl text-xs font-bold">
            {remaining} project(s) remaining
          </span>
        )}
      </div>

      {/* Total Projects Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs font-medium text-slate-300">
          <span>Total Projects: <strong className="text-white">{total} completed</strong></span>
          <span>Required: <strong className="text-white">{required}</strong></span>
        </div>
        <ProgressBar
          value={total}
          max={required || 1}
          color={totalSatisfied ? 'emerald' : 'purple'}
        />
      </div>

      {/* Lead Projects Progress (if required) */}
      {leadRequired > 0 && (
        <div className="space-y-2 pt-2 border-t border-slate-800/80">
          <div className="flex justify-between text-xs font-medium text-slate-300">
            <span>Lead Projects: <strong className="text-white">{leadDone} completed</strong></span>
            <span>Required Lead: <strong className="text-white">{leadRequired}</strong></span>
          </div>
          <ProgressBar
            value={leadDone}
            max={leadRequired}
            color={leadSatisfied ? 'emerald' : 'amber'}
          />
        </div>
      )}
    </div>
  );
};

export default ProjectGapCard;
