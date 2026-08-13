import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getHREmployeeCareerAnalysis, getHREmployeePromotionStatus } from '../api/hrApi';
import { ArrowLeft, User, Award, CheckCircle2, AlertTriangle, Target, TrendingUp } from 'lucide-react';

export const HREmployeeDetailView = () => {
  const { employeeId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [promoStatus, setPromoStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getHREmployeeCareerAnalysis(employeeId),
      getHREmployeePromotionStatus(employeeId),
    ])
      .then(([aRes, pRes]) => {
        setAnalysis(aRes);
        setPromoStatus(pRes);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [employeeId]);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading employee career analysis...</div>;
  }

  if (!analysis) {
    return <div className="p-8 text-center text-red-400">Employee record not found.</div>;
  }

  const emp = analysis.employee || {};
  const readiness = analysis.readiness || {};
  const pred = analysis.prediction || {};

  return (
    <div className="space-y-6">
      <Link to="/hr/employees" className="inline-flex items-center gap-2 text-xs font-semibold text-purple-400 hover:text-purple-300">
        <ArrowLeft className="w-4 h-4" />
        Back to Employee List
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-xl font-bold text-white">{emp.full_name}</h1>
            <p className="text-xs text-slate-400">{emp.email} • {emp.department} • {emp.employee_code}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-indigo-500/20 text-indigo-300 text-xs font-bold rounded-lg">
              {emp.current_grade} → {emp.target_grade}
            </span>
          </div>
        </div>

        {/* HR Third Person Promotion Status Box */}
        {promoStatus && (
          <div className="p-5 bg-slate-950 border border-slate-800 rounded-2xl space-y-3">
            <div className="flex items-start gap-3">
              {promoStatus.is_eligible ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0" />
              )}
              <div>
                <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider">{promoStatus.status_title}</span>
                <h3 className="text-sm font-bold text-white mt-1">{promoStatus.headline}</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Readiness Score: <strong className="text-slate-200">{promoStatus.readiness_text}</strong> • Probability: <strong className="text-purple-300">{promoStatus.promotion_probability_text}</strong>
                </p>
              </div>
            </div>

            {promoStatus.reasons && promoStatus.reasons.length > 0 && (
              <div className="pt-3 border-t border-slate-800">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{promoStatus.gap_headline}</p>
                <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                  {promoStatus.reasons.map((r, idx) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default HREmployeeDetailView;
