import React from 'react';
import { Target, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const GapSummary = ({ gapAnalysis, employeeId = 1 }) => {
  if (!gapAnalysis) return null;

  const skills = gapAnalysis.skills || [];
  const certs = gapAnalysis.certifications || [];
  const exp = gapAnalysis.experience || {};
  const projects = gapAnalysis.projects || {};

  const missingSkillCount = skills.length;
  const missingCertCount = certs.length;
  const expSatisfied = (exp.remaining_years ?? 0) <= 0;
  const remProjects = projects.remaining_projects ?? 0;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Gap Analysis Summary</h3>
            <p className="text-xs text-slate-400">Identified requirements to target grade</p>
          </div>
        </div>
        <Link
          to={`/gap-analysis/${employeeId}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          <span>View Full Gaps</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Skills gap tile */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Skill Gaps</p>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-slate-100">{missingSkillCount}</span>
            {missingSkillCount === 0 ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400" />
            )}
          </div>
          <p className="text-[10px] text-slate-500 mt-1">
            {missingSkillCount === 0 ? 'All skills met' : 'Skill levels needed'}
          </p>
        </div>

        {/* Certification gap tile */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Cert Gaps</p>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-slate-100">{missingCertCount}</span>
            {missingCertCount === 0 ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400" />
            )}
          </div>
          <p className="text-[10px] text-slate-500 mt-1">
            {missingCertCount === 0 ? 'All certs met' : 'Certifications needed'}
          </p>
        </div>

        {/* Experience status tile */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Experience</p>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-sm font-bold text-slate-100">
              {expSatisfied ? 'Met' : `${exp.remaining_years}y left`}
            </span>
            {expSatisfied ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400" />
            )}
          </div>
          <p className="text-[10px] text-slate-500 mt-1">
            Req: {exp.required_years ?? 0} yrs
          </p>
        </div>

        {/* Projects status tile */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Project Gap</p>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-slate-100">{remProjects}</span>
            {remProjects === 0 ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400" />
            )}
          </div>
          <p className="text-[10px] text-slate-500 mt-1">
            {projects.total_projects ?? 0} / {projects.required_projects ?? 0} done
          </p>
        </div>
      </div>
    </div>
  );
};

export default GapSummary;
