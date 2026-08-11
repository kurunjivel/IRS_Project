import React from 'react';

export const Badge = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-slate-700/60 text-slate-300 border-slate-600',
    emerald: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    amber: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    orange: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    rose: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
    indigo: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
    purple: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  };

  const style = variants[variant] || variants.default;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style} ${className}`}
    >
      {children}
    </span>
  );
};

export default Badge;
