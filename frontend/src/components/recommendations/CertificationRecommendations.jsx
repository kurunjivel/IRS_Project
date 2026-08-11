import React from 'react';
import RecommendationCard from './RecommendationCard';
import EmptyState from '../common/EmptyState';
import { Award } from 'lucide-react';

export const CertificationRecommendations = ({ items = [] }) => {
  if (!items || items.length === 0) {
    return (
      <EmptyState
        title="No Certification Recommendations"
        message="All target grade certification requirements are satisfied."
        icon={Award}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {items.map((item, idx) => (
        <RecommendationCard key={idx} item={item} category="Certification" />
      ))}
    </div>
  );
};

export default CertificationRecommendations;
