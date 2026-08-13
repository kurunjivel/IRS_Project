import React, { useState, useEffect } from 'react';
import { getMyPromotionStatus } from '../api/employeePortalApi';
import { Award, CheckCircle2, AlertTriangle } from 'lucide-react';

export const EmployeePromotionStatusView = () => {
  const [promo, setPromo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyPromotionStatus()
      .then(res => setPromo(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading promotion status...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">My Promotion Status</h1>
        <p className="text-xs text-slate-400">Official promotion evaluation report</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <div className="flex items-start gap-4">
          {promo?.is_eligible ? (
            <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0 mt-1" />
          ) : (
            <AlertTriangle className="w-8 h-8 text-amber-400 shrink-0 mt-1" />
          )}
          <div>
            <h2 className="text-lg font-bold text-white">{promo?.headline}</h2>
            <p className="text-xs text-slate-400 mt-1">
              Readiness Score: <strong className="text-slate-200">{promo?.readiness_text}</strong> • Promotion Probability: <strong className="text-indigo-300">{promo?.promotion_probability_text}</strong>
            </p>
          </div>
        </div>

        {promo?.gaps && promo.gaps.length > 0 && (
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">{promo.gap_headline}</h3>
            <div className="space-y-2">
              {promo.gaps.map((g, idx) => (
                <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-200">{g.title}</span>
                  <span className="text-xs font-bold text-indigo-400">{g.detail}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-slate-800 text-xs font-semibold text-indigo-300">
          Recommended Action: <span className="text-slate-200">{promo?.recommended_action}</span>
        </div>
      </div>
    </div>
  );
};

export default EmployeePromotionStatusView;
