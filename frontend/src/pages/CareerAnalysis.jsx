import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PageContainer from '../components/layout/PageContainer';
import { useCareerAnalysis } from '../hooks/useCareerAnalysis';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

import ReadinessCard from '../components/dashboard/ReadinessCard';
import PromotionProbability from '../components/dashboard/PromotionProbability';
import GradeProgress from '../components/dashboard/GradeProgress';
import ReadinessBreakdownChart from '../components/charts/ReadinessBreakdownChart';
import SkillGapCard from '../components/gaps/SkillGapCard';
import CertificationGapCard from '../components/gaps/CertificationGapCard';
import ExperienceGapCard from '../components/gaps/ExperienceGapCard';
import ProjectGapCard from '../components/gaps/ProjectGapCard';
import LearningRecommendations from '../components/recommendations/LearningRecommendations';
import MentorRecommendations from '../components/recommendations/MentorRecommendations';
import CareerTimeline from '../components/timeline/CareerTimeline';
import { TrendingUp, Sparkles, User, Award, Target, Lightbulb, Users, Calendar } from 'lucide-react';
import Badge from '../components/common/Badge';

export const CareerAnalysis = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const empId = Number(employeeId) || 1;

  const { data, loading, error, refetch } = useCareerAnalysis(empId);

  const handleEmployeeChange = (newId) => {
    navigate(`/career-analysis/${newId}`);
  };

  if (loading) {
    return (
      <PageContainer title="Consolidated Career Analysis" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <LoadingSpinner text="Generating comprehensive employee career progression dossier..." />
      </PageContainer>
    );
  }

  if (error || !data) {
    return (
      <PageContainer title="Consolidated Career Analysis" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <ErrorMessage title="Unable to Load Career Dossier" message={error} onRetry={refetch} />
      </PageContainer>
    );
  }

  const { employee, readiness, prediction, gap_analysis, recommendations } = data;

  return (
    <PageContainer title="Consolidated Career Analysis" employeeId={empId} employee={employee} onEmployeeChange={handleEmployeeChange}>
      {/* Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-purple-950/30 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-purple-400 text-xs font-bold uppercase tracking-wider mb-1">
            <TrendingUp className="w-4 h-4" />
            <span>Master Career Progression Dossier</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Career Analysis: {employee?.full_name}</h1>
          <p className="text-xs text-slate-400 mt-1">
            End-to-end HR report synthesizing employee background, readiness metrics, ML predictions, gap audits, and action milestones.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="purple">Employee ID #{empId}</Badge>
          <Badge variant="indigo">{employee?.department}</Badge>
        </div>
      </div>

      {/* SECTION 1: CORE METRICS & PREDICTION */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Award className="w-4 h-4 text-indigo-400" />
          <span>1. Core Readiness & ML Prediction Overview</span>
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ReadinessCard readiness={readiness} />
          <PromotionProbability prediction={prediction} />
          <GradeProgress employee={employee} />
        </div>
      </div>

      {/* SECTION 2: READINESS BREAKDOWN */}
      <div className="space-y-4 pt-4 border-t border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span>2. Evaluation Dimension Breakdown</span>
        </h3>
        <ReadinessBreakdownChart breakdown={readiness?.breakdown} />
      </div>

      {/* SECTION 3: AUDIT GAPS */}
      <div className="space-y-4 pt-4 border-t border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Target className="w-4 h-4 text-amber-400" />
          <span>3. Complete Gap Audit</span>
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase">Skill Gaps</h4>
            <SkillGapCard skills={gap_analysis?.skills} />
          </div>
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase">Certification Gaps</h4>
            <CertificationGapCard certifications={gap_analysis?.certifications} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
          <ExperienceGapCard experience={gap_analysis?.experience} />
          <ProjectGapCard projects={gap_analysis?.projects} />
        </div>
      </div>

      {/* SECTION 4: RECOMMENDATIONS & MENTORS */}
      <div className="space-y-4 pt-4 border-t border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-emerald-400" />
          <span>4. Priority Growth Interventions</span>
        </h3>
        <LearningRecommendations items={recommendations?.learning} />

        <div className="pt-2">
          <h4 className="text-xs font-bold text-slate-300 uppercase mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-emerald-400" />
            <span>Recommended Grade Mentors</span>
          </h4>
          <MentorRecommendations items={recommendations?.mentors} />
        </div>
      </div>

      {/* SECTION 5: CAREER TIMELINE */}
      <div className="space-y-4 pt-4 border-t border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Calendar className="w-4 h-4 text-indigo-400" />
          <span>5. Action Plan Timeline</span>
        </h3>
        <CareerTimeline timeline={recommendations?.timeline} />
      </div>
    </PageContainer>
  );
};

export default CareerAnalysis;
