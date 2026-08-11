import React from 'react';
import { Code, AlertTriangle, CheckCircle2 } from 'lucide-react';
import Badge from '../common/Badge';
import ProgressBar from '../common/ProgressBar';
import EmptyState from '../common/EmptyState';

export const SkillGapCard = ({ skills = [] }) => {
  if (!skills || skills.length === 0) {
    return (
      <EmptyState
        title="All Required Skills Satisfied"
        message="You currently meet or exceed all skill proficiency levels required for your target grade."
        icon={CheckCircle2}
      />
    );
  }

  return (
    <div className="space-y-4">
      {skills.map((item, idx) => {
        const current = item.current_level ?? 0;
        const required = item.required_level ?? 3;
        const gap = item.gap ?? Math.max(required - current, 0);

        return (
          <div
            key={idx}
            className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-md flex flex-col justify-between space-y-3"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
                  <Code className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-base font-bold text-slate-100">{item.skill}</h4>
                    {item.mandatory && (
                      <Badge variant="rose">Mandatory</Badge>
                    )}
                  </div>
                  <p className="text-xs text-slate-400">Category: <span className="text-slate-300 font-medium">{item.category || 'General'}</span></p>
                </div>
              </div>

              <span className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-lg">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Gap: {gap} levels</span>
              </span>
            </div>

            {/* Level progress bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-400 font-medium">
                <span>Proficiency: Level {current} / Level {required}</span>
                <span className="text-slate-300">Level {current} of {required}</span>
              </div>
              <ProgressBar
                value={current}
                max={required}
                color={current === 0 ? 'rose' : 'amber'}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SkillGapCard;
