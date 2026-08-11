export const formatPercentage = (val) => {
  if (val === undefined || val === null) return '0%';
  const num = typeof val === 'number' ? val : parseFloat(val);
  // If probability between 0 and 1, convert to percentage
  const pct = num <= 1.0 ? num * 100 : num;
  return `${pct.toFixed(1)}%`;
};

export const formatScore = (val) => {
  if (val === undefined || val === null) return '0.00';
  const num = typeof val === 'number' ? val : parseFloat(val);
  return num.toFixed(2);
};

export const formatDuration = (duration) => {
  if (!duration) return 'N/A';
  return duration;
};
