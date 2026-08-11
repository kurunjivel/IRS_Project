import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export const EmptyState = ({
  title = 'All Requirements Satisfied',
  message = 'Great job! You have met all criteria for this category.',
  icon: Icon = CheckCircle2,
}) => (
  <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-8 text-center flex flex-col items-center justify-center">
    <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-full mb-3 border border-emerald-500/20">
      <Icon className="w-6 h-6" />
    </div>
    <h4 className="text-base font-semibold text-slate-200">{title}</h4>
    <p className="text-sm text-slate-400 mt-1 max-w-md">{message}</p>
  </div>
);

export default EmptyState;
