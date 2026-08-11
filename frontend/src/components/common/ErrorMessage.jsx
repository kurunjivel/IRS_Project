import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const ErrorMessage = ({
  title = 'Unable to Load Career Data',
  message = 'Please check that the IRS FastAPI backend is running at http://127.0.0.1:8000',
  onRetry,
}) => (
  <div className="bg-rose-950/30 border border-rose-500/30 rounded-xl p-6 text-center max-w-lg mx-auto my-8 shadow-xl">
    <div className="inline-flex p-3 bg-rose-500/10 rounded-full text-rose-400 mb-3 border border-rose-500/20">
      <AlertTriangle className="w-8 h-8" />
    </div>
    <h3 className="text-lg font-semibold text-rose-200">{title}</h3>
    <p className="text-sm text-slate-300 mt-2 mb-4 leading-relaxed">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium text-sm rounded-lg transition-colors shadow-lg shadow-rose-900/30"
      >
        <RefreshCw className="w-4 h-4 animate-spin-hover" />
        Retry Request
      </button>
    )}
  </div>
);

export default ErrorMessage;
