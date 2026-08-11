import React from 'react';
import { Sparkles, Cpu, TrendingUp } from 'lucide-react';
import { formatPercentage } from '../../utils/formatters';
import ProgressBar from '../common/ProgressBar';

export const PromotionProbability = ({ prediction }) => {
  if (!prediction) return null;

  const rawProb = prediction.promotion_probability ?? 0;
  const percentageStr = formatPercentage(rawProb);
  const probVal = rawProb <= 1.0 ? rawProb * 100 : rawProb;
  const label = prediction.prediction || 'Progression Analysis';
  const modelName = prediction.model_name || 'Machine Learning Engine';

  // Color logic for ML probability
  let color = 'indigo';
  let badgeColor = 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
  if (probVal >= 80) {
    color = 'emerald';
    badgeColor = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
  } else if (probVal >= 60) {
    color = 'amber';
    badgeColor = 'bg-amber-500/20 text-amber-300 border-amber-500/30';
  } else {
    color = 'rose';
    badgeColor = 'bg-rose-500/20 text-rose-300 border-rose-500/30';
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden flex flex-col justify-between">
      {/* Top Ambient Glow */}
      <div className="absolute -top-12 -left-12 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-xl">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">ML Promotion Probability</h3>
            <p className="text-xs text-slate-400">Supervised Predictive Classification Model</p>
          </div>
        </div>
        <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${badgeColor}`}>
          {label}
        </span>
      </div>

      {/* Main Score & Progress */}
      <div className="my-4 space-y-4">
        <div className="flex items-baseline justify-between">
          <span className="text-4xl font-extrabold text-white tracking-tight">
            {percentageStr}
          </span>
          <div className="flex items-center gap-1.5 text-xs text-purple-300 font-semibold bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20">
            <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
            <span>Predicted Outcome</span>
          </div>
        </div>

        {/* Visual Progress Bar */}
        <ProgressBar
          value={probVal}
          max={100}
          color={color}
          className="h-3"
        />

        <p className="text-xs text-slate-400 leading-relaxed">
          AI model evaluates performance, experience, project lead roles, and historical promotion patterns.
        </p>
      </div>

      {/* Model Name Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5 text-slate-400">
          <Cpu className="w-3.5 h-3.5 text-slate-400" />
          <span>Classifier: <strong className="text-slate-200">{modelName}</strong></span>
        </div>
        <span className="text-purple-400 font-medium">Phase 5 Model</span>
      </div>
    </div>
  );
};

export default PromotionProbability;
