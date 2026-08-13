import React, { useState, useEffect } from 'react';
import { getMyGapAnalysis } from '../api/employeePortalApi';
import { Target, AlertTriangle, CheckCircle, Code, Award, Briefcase, Clock } from 'lucide-react';

export const EmployeeSkillGapsView = () => {
  const [gaps, setGaps] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyGapAnalysis()
      .then(res => setGaps(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading skill gap analysis...</div>;
  }

  const skillList = gaps?.skills || gaps?.skill_gaps || [];
  const certList = gaps?.certifications || gaps?.certification_gaps || [];
  const exp = gaps?.experience || gaps?.experience_gap || {};
  const proj = gaps?.projects || gaps?.project_gap || {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Skill & Requirement Gap Analysis</h1>
        <p className="text-xs text-slate-400">Identify gaps between your current baseline and target role requirements</p>
      </div>

      {/* Skill Gaps Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <Code className="w-4 h-4 text-indigo-400" />
          Technical Skill Requirements
        </h2>
        <div className="space-y-3">
          {skillList.map((s, idx) => (
            <div key={idx} className="p-4 bg-slate-950 border border-slate-800 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <p className="text-xs font-bold text-slate-200">{s.skill || s.skill_name}</p>
                <p className="text-[11px] text-slate-400">
                  Category: {s.category || 'Core'} • {s.mandatory ? 'Mandatory Requirement' : 'Optional'}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-[11px] font-semibold text-slate-400">
                    Current: Level {s.current_level} / Required: Level {s.required_level}
                  </p>
                </div>
                {s.gap > 0 ? (
                  <span className="px-2.5 py-1 bg-amber-500/20 text-amber-300 text-xs font-bold rounded-lg border border-amber-500/30">
                    Gap: -{s.gap}
                  </span>
                ) : (
                  <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-lg border border-emerald-500/30">
                    Satisfied
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Certifications & Experience Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Award className="w-4 h-4 text-purple-400" />
            Certifications
          </h2>
          <div className="space-y-3">
            {certList.map((c, idx) => (
              <div key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-slate-200">{c.certification || c.certification_name}</p>
                  <p className="text-[10px] text-slate-400">{c.mandatory ? 'Mandatory' : 'Recommended'}</p>
                </div>
                <span className={`px-2.5 py-1 text-xs font-bold rounded-lg ${
                  c.status === 'Completed'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : 'bg-amber-500/20 text-amber-300'
                }`}>
                  {c.status || (c.is_completed ? 'Completed' : 'Missing')}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-indigo-400" />
            Experience & Projects
          </h2>
          <div className="space-y-4">
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl">
              <p className="text-xs font-bold text-slate-300">Experience Requirement</p>
              <p className="text-xs text-slate-400 mt-1">
                Current: {exp.current_years || 0} yrs • Required: {exp.required_years || 0} yrs
              </p>
              {exp.remaining_years > 0 ? (
                <p className="text-xs text-amber-400 font-semibold mt-2">Remaining: {exp.remaining_years} years needed</p>
              ) : (
                <p className="text-xs text-emerald-400 font-semibold mt-2">Requirement met!</p>
              )}
            </div>

            <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl">
              <p className="text-xs font-bold text-slate-300">Project Portfolio</p>
              <p className="text-xs text-slate-400 mt-1">
                Current: {proj.total_projects || 0} projects • Required: {proj.required_projects || 0} projects
              </p>
              {proj.remaining_projects > 0 ? (
                <p className="text-xs text-amber-400 font-semibold mt-2">Remaining: {proj.remaining_projects} projects needed</p>
              ) : (
                <p className="text-xs text-emerald-400 font-semibold mt-2 font-semibold">Portfolio requirement met!</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeSkillGapsView;
