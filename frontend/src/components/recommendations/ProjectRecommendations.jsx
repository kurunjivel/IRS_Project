import React from 'react';
import RecommendationCard from './RecommendationCard';
import EmptyState from '../common/EmptyState';
import { Briefcase } from 'lucide-react';

export const ProjectRecommendations = ({ items = [] }) => {
  if (!items || items.length === 0) {
    return (
      <EmptyState
        title="No Project Recommendations"
        message="You currently meet all required project count and project lead criteria."
        icon={Briefcase}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {items.map((item, idx) => (
        <RecommendationCard key={idx} item={item} category="Project" />
      ))}
    </div>
  );
};

export default ProjectRecommendations;
