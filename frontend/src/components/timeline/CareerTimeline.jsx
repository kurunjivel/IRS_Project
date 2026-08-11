import React from 'react';
import { Calendar, CheckCircle, Flag, BookOpen, Award, Target } from 'lucide-react';
import Badge from '../common/Badge';

export const CareerTimeline = ({ timeline = [] }) => {
  if (!timeline || timeline.length === 0) return null;

  const getCategoryIcon = (category) => {
    switch (category?.toLowerCase()) {
      case 'learning':
        return <BookOpen className="w-4 h-4 text-indigo-400" />;
      case 'certification':
        return <Award className="w-4 h-4 text-amber-400" />;
      case 'readiness':
      case 'target':
        return <Flag className="w-4 h-4 text-emerald-400" />;
      default:
        return <Target className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center gap-2.5 mb-6">
        <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
          <Calendar className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Career Progression Timeline</h3>
          <p className="text-xs text-slate-400">Sequential milestones to achieve target grade readiness</p>
        </div>
      </div>

      <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-8 my-2">
        {timeline.map((step, idx) => {
          const isLast = idx === timeline.length - 1;
          const monthText = typeof step.month === 'number' ? `Month ${step.month}` : step.month || `Phase ${idx + 1}`;

          return (
            <div key={idx} className="relative group">
              {/* Timeline Bullet Node */}
              <div
                className={`absolute -left-[35px] top-0 w-8 h-8 rounded-full flex items-center justify-center border-2 transition-transform duration-200 group-hover:scale-110 ${
                  isLast
                    ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400 shadow-lg shadow-emerald-500/20'
                    : 'bg-slate-900 border-indigo-500 text-indigo-400'
                }`}
              >
                {getCategoryIcon(step.category)}
              </div>

              {/* Card Container */}
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 shadow-md space-y-2 hover:border-slate-700 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full border border-indigo-500/20">
                    {monthText}
                  </span>
                  <Badge variant={isLast ? 'emerald' : 'indigo'}>
                    {step.category || 'Milestone'}
                  </Badge>
                </div>

                <h4 className="text-sm font-bold text-slate-100">{step.title}</h4>
                <p className="text-xs text-slate-300 leading-relaxed">{step.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CareerTimeline;
