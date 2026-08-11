import React from 'react';
import { Award, CheckCircle2, AlertCircle } from 'lucide-react';
import Badge from '../common/Badge';
import EmptyState from '../common/EmptyState';

export const CertificationGapCard = ({ certifications = [] }) => {
  if (!certifications || certifications.length === 0) {
    return (
      <EmptyState
        title="All Certification Requirements Satisfied"
        message="All required and recommended certifications for your target grade have been completed."
        icon={CheckCircle2}
      />
    );
  }

  return (
    <div className="space-y-4">
      {certifications.map((cert, idx) => (
        <div
          key={idx}
          className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-md flex items-center justify-between"
        >
          <div className="flex items-center gap-3.5">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-base font-bold text-slate-100">{cert.certification}</h4>
                {cert.mandatory ? (
                  <Badge variant="rose">Mandatory</Badge>
                ) : (
                  <Badge variant="amber">Recommended</Badge>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Provider: <span className="text-slate-200 font-medium">{cert.provider || 'Internal / Partner'}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl text-xs font-semibold">
            <AlertCircle className="w-4 h-4" />
            <span>Missing</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CertificationGapCard;
