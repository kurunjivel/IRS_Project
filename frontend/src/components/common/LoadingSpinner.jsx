import React from 'react';

export const LoadingSpinner = ({ text = 'Loading career data...' }) => (
  <div className="flex flex-col items-center justify-center min-h-[300px] p-8 text-slate-400">
    <div className="relative flex items-center justify-center">
      <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
      <div className="absolute w-6 h-6 border-4 border-purple-500/20 border-b-purple-500 rounded-full animate-spin animate-reverse"></div>
    </div>
    <p className="mt-4 text-sm font-medium tracking-wide text-slate-300 animate-pulse">{text}</p>
  </div>
);

export const SkeletonCard = ({ height = 'h-32' }) => (
  <div className={`bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 animate-pulse ${height}`}>
    <div className="h-4 bg-slate-700/60 rounded w-1/3 mb-4"></div>
    <div className="h-8 bg-slate-700/40 rounded w-1/2 mb-2"></div>
    <div className="h-3 bg-slate-700/30 rounded w-2/3"></div>
  </div>
);

export default LoadingSpinner;
