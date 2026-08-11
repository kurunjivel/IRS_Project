import React from 'react';
import { Award, ShieldCheck } from 'lucide-react';
import { getReadinessStatus, getDecisionBadge } from '../../utils/readiness';
import { formatScore } from '../../utils/formatters';

export const ReadinessCard = ({ readiness }) => {
  if (!readiness) return null;

  const score = readiness.readiness_score || 0;
  const level = readiness.readiness_level || 'Calculating...';
  const decision = readiness.promotion_decision || 'Pending';
  const status = getReadinessStatus(score);
  const decisionStyle = getDecisionBadge(decision);

  // SVG Circular Gauge calculation
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden flex flex-col justify-between">
      {/* Background ambient glow */}
      <div
        className="absolute -top-12 -right-12 w-40 h-40 rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{ backgroundColor: status.strokeColor }}
      />

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Overall Readiness</h3>
            <p className="text-xs text-slate-400">Calculated score based on gaps & weightages</p>
          </div>
        </div>
        <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${decisionStyle}`}>
          {decision}
        </span>
      </div>

      {/* Circle Gauge & Content */}
      <div className="flex flex-col sm:flex-row items-center justify-around gap-6 my-4">
        {/* SVG Circular Progress */}
        <div className="relative w-36 h-36 flex items-center justify-center shrink-0">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 128 128">
            {/* Background circle */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              className="stroke-slate-800"
              strokeWidth="10"
              fill="transparent"
            />
            {/* Value circle */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke={status.strokeColor}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-3xl font-extrabold text-slate-100 tracking-tight">
              {formatScore(score)}
            </span>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mt-0.5">
              out of 100
            </span>
          </div>
        </div>

        {/* Level & Decision info */}
        <div className="flex flex-col items-center sm:items-start text-center sm:text-left space-y-3">
          <div>
            <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Readiness Level</p>
            <span className={`inline-block mt-1 px-3 py-1 rounded-lg text-sm font-bold border ${status.badge}`}>
              {level}
            </span>
          </div>

          <div className="pt-1 border-t border-slate-800/80 w-full">
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <ShieldCheck className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>Decision: <strong className="text-slate-100 font-semibold">{decision}</strong></span>
            </div>
          </div>
        </div>
      </div>

      <div className="text-[11px] text-slate-500 text-center sm:text-left pt-2 border-t border-slate-800">
        Updated in real-time based on career gap & readiness engine
      </div>
    </div>
  );
};

export default ReadinessCard;
