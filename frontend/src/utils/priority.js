export const getPriorityClass = (priority) => {
  switch (priority?.toUpperCase()) {
    case 'HIGH':
      return {
        bg: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
        dot: 'bg-rose-500',
        text: 'text-rose-400',
        cardBorder: 'border-l-4 border-l-rose-500',
      };
    case 'MEDIUM':
      return {
        bg: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
        dot: 'bg-amber-500',
        text: 'text-amber-400',
        cardBorder: 'border-l-4 border-l-amber-500',
      };
    case 'LOW':
    default:
      return {
        bg: 'bg-slate-700/60 text-slate-300 border-slate-600',
        dot: 'bg-slate-400',
        text: 'text-slate-300',
        cardBorder: 'border-l-4 border-l-slate-600',
      };
  }
};
