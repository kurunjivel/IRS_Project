import React from 'react';
import RecommendationCard from './RecommendationCard';
import EmptyState from '../common/EmptyState';
import { BookOpen } from 'lucide-react';

export const LearningRecommendations = ({ items = [] }) => {
  if (!items || items.length === 0) {
    return (
      <EmptyState
        title="No Learning Recommendations"
        message="No mandatory skill gap learning paths required at this time."
        icon={BookOpen}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {items.map((item, idx) => (
        <RecommendationCard key={idx} item={item} category="Learning" />
      ))}
    </div>
  );
};

export default LearningRecommendations;
