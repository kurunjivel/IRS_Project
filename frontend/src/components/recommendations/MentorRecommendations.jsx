import React from 'react';
import { Users, Mail, Award, CheckCircle, ArrowUpRight } from 'lucide-react';
import PriorityBadge from './PriorityBadge';
import EmptyState from '../common/EmptyState';

export const MentorRecommendations = ({ items = [] }) => {
  if (!items || items.length === 0) {
    return (
      <EmptyState
        title="No Mentor Recommendations"
        message="No matching available mentors found for target grade level."
        icon={Users}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {items.map((item, idx) => {
        const meta = item.metadata || {};
        const name = meta.full_name || item.title.replace('Connect with mentor: ', '');
        const grade = meta.current_grade || 'Senior';
        const dept = meta.department || 'Engineering';
        const spec = meta.specialisation || meta.specialization || 'Technical Leadership';
        const email = meta.email || `${name.toLowerCase().replace(' ', '.')}@company.com`;
        const priority = item.priority || 'LOW';

        return (
          <div
            key={idx}
            className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg backdrop-blur-sm flex flex-col justify-between space-y-4 hover:border-indigo-500/40 transition-all duration-200"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-600 flex items-center justify-center text-white font-bold text-lg shadow-md">
                    {name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-100">{name}</h4>
                    <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
                      <Award className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{grade} • {dept}</span>
                    </p>
                  </div>
                </div>
                <PriorityBadge priority={priority} />
              </div>

              <p className="text-xs text-slate-300 bg-slate-950/40 p-3 rounded-xl border border-slate-800/60 leading-relaxed">
                {item.reason}
              </p>

              <div className="space-y-1.5 pt-1 text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Specialisation:</span>
                  <strong className="text-slate-200 font-semibold">{spec}</strong>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Availability:</span>
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <CheckCircle className="w-3.5 h-3.5" />
                    Available for Mentoring
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Contact:</span>
                  <span className="text-indigo-300 font-mono text-[11px]">{email}</span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => alert(`Connecting with mentor: ${name} (${email})`)}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow-md shadow-indigo-600/20"
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Connect with Mentor</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MentorRecommendations;
