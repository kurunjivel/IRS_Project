import React, { useState, useEffect } from 'react';
import { getMyAttritionRisk } from '../api/employeePortalApi';
import { ShieldCheck, TrendingUp, Sparkles, CheckCircle2, AlertCircle, Info, ArrowUpRight, HelpCircle } from 'lucide-react';

export const EmployeeCareerStabilityView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyAttritionRisk()
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Evaluating career stability indicators...</div>;
  }

  if (!data) {
    return <div className="p-6 bg-slate-900 border border-slate-800 text-slate-300 rounded-2xl">Unable to load career stability indicators.</div>;
  }

  const riskLevel = data.risk_level || 'LOW';
  const riskProb = data.risk_probability || 0.2;

  // Non-alarming styling & text
  const stabilityBadge = riskLevel === 'LOW'
    ? { title: 'High Career Stability', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' }
    : riskLevel === 'MODERATE'
    ? { title: 'Optimal Growth Pace', color: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20' }
    : { title: 'Actionable Growth Opportunity', color: 'bg-amber-500/10 text-amber-300 border-amber-500/20' };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
            Career Stability & Growth Indicators
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Personalized career continuity analysis for <span className="text-slate-200 font-semibold">{data.full_name}</span> ({data.current_grade} → {data.target_grade})
          </p>
        </div>
        <span className={`px-3 py-1.5 border text-xs font-bold rounded-full ${stabilityBadge.color}`}>
          {stabilityBadge.title}
        </span>
      </div>

      {/* Main Stability Summary Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-2xl">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Stability Rating</span>
            <p className="text-2xl font-extrabold text-white mt-1">{stabilityBadge.title}</p>
            <p className="text-[11px] text-slate-400 mt-1">Model Version: {data.model_version}</p>
          </div>

          <div className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-2xl">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Flight-Risk Factor</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-extrabold text-indigo-300">{(riskProb * 100).toFixed(0)}%</span>
              <span className="text-xs text-slate-400">({riskLevel} RISK)</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className={`h-full rounded-full ${riskLevel === 'LOW' ? 'bg-emerald-400' : riskLevel === 'MODERATE' ? 'bg-indigo-400' : 'bg-amber-400'}`}
                style={{ width: `${Math.min(100, riskProb * 100)}%` }}
              />
            </div>
          </div>

          <div className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-2xl">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Evaluation Method</span>
            <p className="text-xs font-semibold text-purple-300 mt-1">{data.model_status}</p>
            <p className="text-[10px] text-slate-400 mt-1 leading-tight">Legitimate career signal evaluation</p>
          </div>
        </div>

        {/* Data Readiness Audit Report Pill */}
        <div className="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl text-xs text-slate-300 flex items-start gap-3">
          <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
          <div>
            <strong className="text-indigo-200">Data Readiness Audit:</strong> {data.data_readiness_report}
          </div>
        </div>
      </div>

      {/* Contributing Factors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Positive Factors (Supporting Stability) */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Factors Supporting Career Stability ({data.positive_factors?.length || 0})
          </h2>
          <div className="space-y-3">
            {data.positive_factors?.map((f, idx) => (
              <div key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-emerald-300">{f.feature_name}</span>
                  <span className="text-[10px] font-semibold text-slate-400">-{ (f.impact_magnitude * 100).toFixed(0) }% Risk</span>
                </div>
                <p className="text-[11px] text-slate-400">{f.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Negative Risk Factors (Growth Areas) */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            Flight-Risk Growth Indicators ({data.negative_factors?.length || 0})
          </h2>
          <div className="space-y-3">
            {data.negative_factors?.map((f, idx) => (
              <div key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-amber-300">{f.feature_name}</span>
                  <span className="text-[10px] font-semibold text-amber-400">+{ (f.impact_magnitude * 100).toFixed(0) }% Risk</span>
                </div>
                <p className="text-[11px] text-slate-400">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommended Career Growth Actions */}
      {data.recommended_career_actions && data.recommended_career_actions.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-3">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Recommended Career Growth Actions
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {data.recommended_career_actions.map((act, i) => (
              <div key={i} className="p-3.5 bg-slate-950 border border-slate-800 rounded-2xl flex items-start gap-2.5 text-xs text-slate-300">
                <ArrowUpRight className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <span>{act}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployeeCareerStabilityView;
