import React from 'react';
import { useSearchParams } from 'react-router-dom';
import PageContainer from '../components/layout/PageContainer';
import { useCareerAnalysis } from '../hooks/useCareerAnalysis';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

// Dashboard components
import QuickStats from '../components/dashboard/QuickStats';
import ReadinessCard from '../components/dashboard/ReadinessCard';
import PromotionProbability from '../components/dashboard/PromotionProbability';
import GradeProgress from '../components/dashboard/GradeProgress';
import GapSummary from '../components/dashboard/GapSummary';

// Charts & Details
import ReadinessBreakdownChart from '../components/charts/ReadinessBreakdownChart';
import SkillGapCard from '../components/gaps/SkillGapCard';
import RecommendationPriorityChart from '../components/charts/RecommendationPriorityChart';
import LearningRecommendations from '../components/recommendations/LearningRecommendations';
import CareerTimeline from '../components/timeline/CareerTimeline';
import { ArrowRight, Sparkles, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const employeeId = Number(searchParams.get('employee')) || 1;

  const { data, loading, error, refetch } = useCareerAnalysis(employeeId);

  const handleEmployeeChange = (newId) => {
    setSearchParams({ employee: newId });
  };

  if (loading) {
    return (
      <PageContainer
        title="Career Progression Dashboard"
        employeeId={employeeId}
        onEmployeeChange={handleEmployeeChange}
      >
        <LoadingSpinner text="Fetching real-time career metrics and recommendations..." />
      </PageContainer>
    );
  }

  if (error || !data) {
    return (
      <PageContainer
        title="Career Progression Dashboard"
        employeeId={employeeId}
        onEmployeeChange={handleEmployeeChange}
      >
        <ErrorMessage
          title="Backend Connection Error"
          message={error || 'Unable to fetch career analysis from FastAPI backend at http://127.0.0.1:8000'}
          onRetry={refetch}
        />
      </PageContainer>
    );
  }

  const { employee, readiness, prediction, gap_analysis, recommendations } = data;

  return (
    <PageContainer
      title="Career Progression Dashboard"
      employeeId={employeeId}
      employee={employee}
      onEmployeeChange={handleEmployeeChange}
    >
      {/* HERO SECTION */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Intelligent Career Recommendation Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Welcome back, {employee?.full_name || 'Employee'}
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Track your progression criteria, readiness score, skill gaps, and AI-recommended growth path for your target grade.
          </p>
        </div>

        {/* Grade transition hero badge */}
        <div className="flex items-center gap-3 bg-slate-950/80 border border-slate-800 px-4 py-2.5 rounded-xl shrink-0">
          <div className="text-center">
            <span className="text-[10px] text-slate-500 font-bold block uppercase">Current</span>
            <span className="text-lg font-black text-slate-200">{employee?.current_grade}</span>
          </div>
          <ChevronRight className="w-5 h-5 text-indigo-400" />
          <div className="text-center">
            <span className="text-[10px] text-indigo-400 font-bold block uppercase">Target</span>
            <span className="text-lg font-black text-indigo-300">{employee?.target_grade}</span>
          </div>
        </div>
      </div>

      {/* QUICK STATS BAR */}
      <QuickStats recommendations={recommendations} />

      {/* 3 CORE METRIC CARDS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ReadinessCard readiness={readiness} />
        <PromotionProbability prediction={prediction} />
        <GradeProgress employee={employee} />
      </div>

      {/* READINESS BREAKDOWN & GAP SUMMARY */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ReadinessBreakdownChart breakdown={readiness?.breakdown} />
        </div>
        <div className="lg:col-span-1">
          <RecommendationPriorityChart summary={recommendations?.summary} />
        </div>
      </div>

      {/* GAP SUMMARY & SKILL GAPS PREVIEW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <GapSummary gapAnalysis={gap_analysis} employeeId={employeeId} />
        </div>
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Identified Skill Gaps</h3>
            <Link
              to={`/gap-analysis/${employeeId}`}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            >
              View All Gaps <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <SkillGapCard skills={gap_analysis?.skills} />
        </div>
      </div>

      {/* TOP RECOMMENDATIONS PREVIEW & TIMELINE */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Priority Recommendations</h3>
            <Link
              to={`/recommendations/${employeeId}`}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            >
              Explore All Recommendations <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <LearningRecommendations items={recommendations?.learning?.slice(0, 2)} />
        </div>

        <div className="lg:col-span-1">
          <CareerTimeline timeline={recommendations?.timeline} />
        </div>
      </div>
    </PageContainer>
  );
};

export default Dashboard;
