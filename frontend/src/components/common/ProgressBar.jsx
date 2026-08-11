import React from 'react';

export const ProgressBar = ({
  value = 0,
  max = 100,
  color = 'indigo',
  showText = false,
  label = '',
  className = '',
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const colors = {
    indigo: 'bg-indigo-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
    orange: 'bg-orange-500',
    rose: 'bg-rose-500',
    purple: 'bg-purple-500',
    blue: 'bg-sky-500',
  };

  const barColor = colors[color] || colors.indigo;

  return (
    <div className={`w-full ${className}`}>
      {(label || showText) && (
        <div className="flex justify-between items-center text-xs font-medium text-slate-300 mb-1.5">
          <span>{label}</span>
          {showText && <span>{percentage.toFixed(0)}%</span>}
        </div>
      )}
      <div className="w-full bg-slate-700/60 rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-full ${barColor} transition-all duration-500 ease-out rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
