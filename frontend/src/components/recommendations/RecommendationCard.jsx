import React from 'react';
import { BookOpen, Award, Briefcase, Users, Clock, Zap, ArrowUpRight } from 'lucide-react';
import PriorityBadge from './PriorityBadge';
import { getPriorityClass } from '../../utils/priority';

export const RecommendationCard = ({ item, category = 'Learning' }) => {
  if (!item) return null;

  const priority = item.priority || 'LOW';
  const pStyle = getPriorityClass(priority);

  // Category Icon map
  const getIcon = () => {
    switch (category.toLowerCase()) {
      case 'learning':
        return <BookOpen className="w-5 h-5 text-indigo-400" />;
      case 'certification':
        return <Award className="w-5 h-5 text-amber-400" />;
      case 'project':
        return <Briefcase className="w-5 h-5 text-purple-400" />;
      case 'mentorship':
      case 'mentor':
        return <Users className="w-5 h-5 text-emerald-400" />;
      default:
        return <Zap className="w-5 h-5 text-blue-400" />;
    }
  };

  const getActionButtonText = () => {
    switch (category.toLowerCase()) {
      case 'learning':
        return 'Start Learning';
      case 'certification':
        return 'View Certification Details';
      case 'project':
        return 'View Project Listing';
      case 'mentorship':
      case 'mentor':
        return 'Connect with Mentor';
      default:
        return 'Take Action';
    }
  };

  return (
    <div className={`bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg backdrop-blur-sm flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all duration-200 ${pStyle.cardBorder}`}>
      <div className="space-y-3">
        {/* Top Header Row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-slate-800/80 border border-slate-700/80 rounded-xl">
              {getIcon()}
            </div>
            <div>
              <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                {category} Recommendation
              </span>
              <h4 className="text-base font-bold text-slate-100 leading-snug">{item.title}</h4>
            </div>
          </div>
          <PriorityBadge priority={priority} />
        </div>

        {/* Reason / Rationale */}
        <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-3 rounded-xl border border-slate-800/60">
          {item.reason}
        </p>

        {/* Metadata grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs pt-1">
          {item.provider && (
            <div className="bg-slate-800/30 p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Provider</span>
              <span className="font-semibold text-slate-200">{item.provider}</span>
            </div>
          )}
          {item.duration && (
            <div className="bg-slate-800/30 p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Duration</span>
              <span className="font-semibold text-slate-200 flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-400" />
                {item.duration}
              </span>
            </div>
          )}
          {item.impact && (
            <div className="bg-slate-800/30 p-2 rounded-lg border border-slate-800 col-span-2 sm:col-span-1">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Expected Impact</span>
              <span className="font-semibold text-emerald-400 flex items-center gap-1 truncate">
                <Zap className="w-3 h-3 text-emerald-400" />
                {item.impact}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
        <span className="text-[11px] text-slate-500 font-medium">IRS Engine Generated</span>
        <button
          onClick={() => alert(`Initiated action: ${item.title}`)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors border border-slate-700 shadow-sm"
        >
          <span>{getActionButtonText()}</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};

export default RecommendationCard;
