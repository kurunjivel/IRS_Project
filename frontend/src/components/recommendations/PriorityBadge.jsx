import React from 'react';
import { getPriorityClass } from '../../utils/priority';

export const PriorityBadge = ({ priority = 'LOW' }) => {
  const pStyle = getPriorityClass(priority);

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border ${pStyle.bg}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${pStyle.dot}`} />
      <span>{priority.toUpperCase()} PRIORITY</span>
    </span>
  );
};

export default PriorityBadge;
