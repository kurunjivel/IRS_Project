import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PageContainer from '../components/layout/PageContainer';
import { useCareerAnalysis } from '../hooks/useCareerAnalysis';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import SkillGapCard from '../components/gaps/SkillGapCard';
import CertificationGapCard from '../components/gaps/CertificationGapCard';
import ExperienceGapCard from '../components/gaps/ExperienceGapCard';
import ProjectGapCard from '../components/gaps/ProjectGapCard';
import SkillGapChart from '../components/charts/SkillGapChart';
import { Target, Code, Award, Clock, Briefcase, CheckCircle2 } from 'lucide-react';

export const GapAnalysis = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const empId = Number(employeeId) || 1;

  const { data, loading, error, refetch } = useCareerAnalysis(empId);

  const handleEmployeeChange = (newId) => {
    navigate(`/gap-analysis/${newId}`);
  };

  if (loading) {
    return (
      <PageContainer title="Gap Analysis" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <LoadingSpinner text="Computing grade requirement gap analysis..." />
      </PageContainer>
    );
  }

  if (error || !data) {
    return (
      <PageContainer title="Gap Analysis" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <ErrorMessage title="Unable to Load Gap Analysis" message={error} onRetry={refetch} />
      </PageContainer>
    );
  }

  const { employee, gap_analysis } = data;
  const skills = gap_analysis?.skills || [];
  const certs = gap_analysis?.certifications || [];
  const exp = gap_analysis?.experience || {};
  const projects = gap_analysis?.projects || {};

  const expSatisfied = (exp.remaining_years ?? 0) <= 0;

  return (
    <PageContainer title="Gap Analysis" employeeId={empId} employee={employee} onEmployeeChange={handleEmployeeChange}>
      {/* Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Target className="w-4 h-4" />
            <span>Target Grade Requirements Audit</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Gap Analysis: {employee?.current_grade} → {employee?.target_grade}</h1>
          <p className="text-xs text-slate-400 mt-1">
            Comparing current employee capabilities against target grade prerequisites across skills, certifications, tenure, and projects.
          </p>
        </div>
      </div>

      {/* TOP SUMMARY CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Code className="w-5 h-5 text-indigo-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Total Skill Gaps</p>
            <p className="text-xl font-bold text-slate-100">{skills.length}</p>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Award className="w-5 h-5 text-amber-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Cert Gaps</p>
            <p className="text-xl font-bold text-slate-100">{certs.length}</p>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Clock className="w-5 h-5 text-blue-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Experience Status</p>
            <p className="text-sm font-bold text-slate-100">{expSatisfied ? 'Satisfied' : `${exp.remaining_years}y needed`}</p>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Briefcase className="w-5 h-5 text-purple-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Project Gaps</p>
            <p className="text-xl font-bold text-slate-100">{projects.remaining_projects ?? 0}</p>
          </div>
        </div>
      </div>

      {/* SECTION 1: SKILL GAPS */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <Code className="w-5 h-5 text-indigo-400" />
          <span>1. Technical & Functional Skill Gaps</span>
        </h3>
        {skills.length > 0 && <SkillGapChart skills={skills} />}
        <SkillGapCard skills={skills} />
      </div>

      {/* SECTION 2: CERTIFICATION GAPS */}
      <div className="space-y-4 pt-4 border-t border-slate-800">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-400" />
          <span>2. Certification Requirements Gaps</span>
        </h3>
        <CertificationGapCard certifications={certs} />
      </div>

      {/* SECTION 3: EXPERIENCE & PROJECT GAPS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
        <div className="space-y-3">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            <span>3. Experience Tenure Requirement</span>
          </h3>
          <ExperienceGapCard experience={exp} />
        </div>

        <div className="space-y-3">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-purple-400" />
            <span>4. Project Portfolio Requirement</span>
          </h3>
          <ProjectGapCard projects={projects} />
        </div>
      </div>
    </PageContainer>
  );
};

export default GapAnalysis;
