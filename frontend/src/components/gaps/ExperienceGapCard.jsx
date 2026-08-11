import React from 'react';
import { Clock, CheckCircle2 } from 'lucide-react';
import ProgressBar from '../common/ProgressBar';

export const ExperienceGapCard = ({ experience }) => {
  if (!experience) return null;

  const current = experience.current_years ?? 0;
  const required = experience.required_years ?? 0;
  const remaining = experience.remaining_years ?? 0;
  const satisfied = remaining <= 0;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-xl">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-base font-bold text-slate-100">Experience Requirement</h4>
            <p className="text-xs text-slate-400">Total domain and industry tenure</p>
          </div>
        </div>

        {satisfied ? (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl text-xs font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Satisfied</span>
          </span>
        ) : (
          <span className="px-3 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-xl text-xs font-bold">
            {remaining} yrs remaining
          </span>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-xs font-medium text-slate-300">
          <span>Current: <strong className="text-white">{current} yrs</strong></span>
          <span>Target Required: <strong className="text-white">{required} yrs</strong></span>
        </div>
        <ProgressBar
          value={current}
          max={required || 1}
          color={satisfied ? 'emerald' : 'blue'}
        />
      </div>

      <p className="text-xs text-slate-400">
        {satisfied
          ? 'Experience tenure requirement for target grade is fully satisfied.'
          : `You need ${remaining} additional years of experience to meet the baseline requirement for your target grade.`}
      </p>
    </div>
  );
};

export default ExperienceGapCard;
