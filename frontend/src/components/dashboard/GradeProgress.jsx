import React from 'react';
import { ArrowRight, UserCheck, Briefcase, Star, Clock } from 'lucide-react';

export const GradeProgress = ({ employee }) => {
  if (!employee) return null;

  const currentGrade = employee.current_grade || 'N/A';
  const targetGrade = employee.target_grade || 'N/A';
  const exp = employee.experience_years ? `${employee.experience_years} yrs` : 'N/A';
  const rating = employee.performance_rating ? `${employee.performance_rating} / 5` : 'N/A';
  const dept = employee.department || 'Corporate';

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-xl">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Target Progression</h3>
            <p className="text-xs text-slate-400">Career path grade transition</p>
          </div>
        </div>
        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
          {dept}
        </span>
      </div>

      {/* Visual Arrow Transition */}
      <div className="my-3 p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex items-center justify-around">
        <div className="text-center">
          <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider mb-1">Current Grade</span>
          <div className="w-14 h-14 bg-slate-800 border border-slate-700 rounded-2xl flex items-center justify-center text-xl font-black text-slate-200 shadow-md">
            {currentGrade}
          </div>
        </div>

        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-1.5 text-indigo-400 font-bold text-xs">
            <span>Progressing</span>
            <ArrowRight className="w-5 h-5 animate-pulse text-indigo-400" />
          </div>
          <div className="h-1 w-20 sm:w-28 bg-gradient-to-r from-slate-700 via-indigo-500 to-indigo-400 rounded-full" />
        </div>

        <div className="text-center">
          <span className="text-[10px] uppercase font-bold text-indigo-400 block tracking-wider mb-1">Target Grade</span>
          <div className="w-14 h-14 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center text-xl font-black text-white shadow-lg shadow-indigo-600/30">
            {targetGrade}
          </div>
        </div>
      </div>

      {/* Profile quick stats */}
      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800 text-xs">
        <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-800/40 border border-slate-800">
          <Clock className="w-4 h-4 text-slate-400 shrink-0" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Experience</p>
            <p className="font-semibold text-slate-200">{exp}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-800/40 border border-slate-800">
          <Star className="w-4 h-4 text-amber-400 shrink-0" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Rating</p>
            <p className="font-semibold text-slate-200">{rating}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GradeProgress;
