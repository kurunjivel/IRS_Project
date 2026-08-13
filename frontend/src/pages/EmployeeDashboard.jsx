import React, { useState, useEffect } from 'react';
import { getMyCareerAnalysis, getMyPromotionStatus } from '../api/employeePortalApi';
import {
  Sparkles,
  Award,
  TrendingUp,
  Target,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  ArrowUpRight,
  Clock,
  Layers,
} from 'lucide-react';

export const EmployeeDashboard = () => {
  const [data, setData] = useState(null);
  const [promoStatus, setPromoStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [analysisRes, statusRes] = await Promise.all([
          getMyCareerAnalysis(),
          getMyPromotionStatus(),
        ]);
        setData(analysisRes);
        setPromoStatus(statusRes);
      } catch (err) {
        console.error('Failed to load employee dashboard data:', err);
        setError('Failed to load your career profile data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-300 text-xs font-semibold">
        {error || 'Unable to display dashboard data.'}
      </div>
    );
  }

  const emp = data.employee || {};
  const readiness = data.readiness || {};
  const prediction = data.prediction || {};
  const recs = data.recommendations || {};
  const gaps = data.gap_analysis || {};

  return (
    <div className="space-y-8">
      {/* Welcome Hero Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-900/80 via-slate-900 to-purple-900/80 border border-indigo-500/20 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/30 rounded-full text-xs font-semibold text-indigo-300 mb-3">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              IRS Personalized Career Intelligence
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {emp.full_name || 'Team Member'}!
            </h1>
            <p className="text-xs text-slate-300 mt-2 max-w-xl">
              Track your grade progression, address skill gaps, and explore AI-powered recommendations to qualify for your target promotion.
            </p>
          </div>

          <div className="flex items-center gap-4 bg-slate-950/60 border border-slate-800 p-4 rounded-2xl shrink-0">
            <div className="text-center px-3 border-r border-slate-800">
              <p className="text-[10px] uppercase font-bold text-slate-400">Current Grade</p>
              <p className="text-xl font-extrabold text-indigo-400">{emp.current_grade}</p>
            </div>
            <ChevronRight className="w-5 h-5 text-slate-600" />
            <div className="text-center px-3">
              <p className="text-[10px] uppercase font-bold text-slate-400">Target Grade</p>
              <p className="text-xl font-extrabold text-purple-400">{emp.target_grade}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Top Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Readiness Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Readiness Score</span>
            <Target className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{readiness.readiness_score?.toFixed(1) || '0.0'}</span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, readiness.readiness_score || 0)}%` }}
            />
          </div>
        </div>

        {/* Promotion Probability Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Promotion Probability</span>
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {((prediction.promotion_probability || 0) * 100).toFixed(1)}%
            </span>
          </div>
          <p className="text-[11px] text-purple-300 mt-2 font-medium">
            Predictive Model: {prediction.prediction || 'Progression Analysis'}
          </p>
        </div>

        {/* Status Badge Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Eligibility Decision</span>
            <Award className="w-5 h-5 text-emerald-400" />
          </div>
          <span
            className={`inline-block px-3 py-1 rounded-lg text-xs font-bold ${
              promoStatus?.is_eligible
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
            }`}
          >
            {promoStatus?.eligibility_text || readiness.promotion_decision || 'Conditional'}
          </span>
          <p className="text-[11px] text-slate-400 mt-2 font-medium">
            {readiness.readiness_level || 'Almost Ready'}
          </p>
        </div>

        {/* Action Items Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Action Items</span>
            <BookOpen className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {recs.summary?.total || (recs.learning?.length || 0) + (recs.projects?.length || 0)}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">Identified career development actions</p>
        </div>
      </div>

      {/* Promotion Status Section (FIRST PERSON MESSAGING) */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">
              {promoStatus?.status_title || 'YOUR PROMOTION STATUS'}
            </h2>
            <p className="text-xs text-slate-400">Direct status evaluation generated for you</p>
          </div>
        </div>

        <div className="p-5 bg-slate-950/80 border border-slate-800/80 rounded-2xl space-y-4">
          <div className="flex items-start gap-3">
            {promoStatus?.is_eligible ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
            )}
            <div>
              <h3 className="text-sm font-bold text-slate-100">{promoStatus?.headline}</h3>
              <p className="text-xs text-slate-400 mt-1">
                Readiness Score: <strong className="text-slate-200">{promoStatus?.readiness_text}</strong> • Promotion Probability: <strong className="text-indigo-300">{promoStatus?.promotion_probability_text}</strong>
              </p>
            </div>
          </div>

          {promoStatus?.gaps && promoStatus.gaps.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-800">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                {promoStatus.gap_headline}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {promoStatus.gaps.map((item, idx) => (
                  <div key={idx} className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-200">{item.title}</span>
                    <span className="text-[11px] font-bold text-indigo-400">{item.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="pt-3 flex items-center gap-2 text-xs font-semibold text-indigo-300">
            <span>Recommended Action:</span>
            <span className="text-slate-200">{promoStatus?.recommended_action}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDashboard;
