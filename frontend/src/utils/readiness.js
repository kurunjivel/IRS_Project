export const getReadinessStatus = (score) => {
  if (score >= 85) {
    return {
      label: 'Ready',
      color: 'emerald',
      bgClass: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
      strokeColor: '#10b981',
      badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    };
  }
  if (score >= 70) {
    return {
      label: 'Almost Ready',
      color: 'amber',
      bgClass: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      strokeColor: '#f59e0b',
      badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    };
  }
  if (score >= 50) {
    return {
      label: 'Needs Improvement',
      color: 'orange',
      bgClass: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
      strokeColor: '#f97316',
      badge: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    };
  }
  return {
    label: 'Significant Gaps',
    color: 'red',
    bgClass: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
    strokeColor: '#f43f5e',
    badge: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  };
};

export const getDecisionBadge = (decision) => {
  switch (decision?.toLowerCase()) {
    case 'ready':
    case 'approved':
      return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    case 'conditional':
      return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    case 'not ready':
    case 'rejected':
      return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    default:
      return 'bg-slate-700 text-slate-300 border-slate-600';
  }
};
