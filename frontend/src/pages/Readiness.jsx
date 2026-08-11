import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PageContainer from '../components/layout/PageContainer';
import { useCareerAnalysis } from '../hooks/useCareerAnalysis';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import ReadinessCard from '../components/dashboard/ReadinessCard';
import ReadinessBreakdownChart from '../components/charts/ReadinessBreakdownChart';
import { Award, HelpCircle, ShieldAlert, CheckCircle2 } from 'lucide-react';
import Badge from '../components/common/Badge';

export const Readiness = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const empId = Number(employeeId) || 1;

  const { data, loading, error, refetch } = useCareerAnalysis(empId);

  const handleEmployeeChange = (newId) => {
    navigate(`/readiness/${newId}`);
  };

  if (loading) {
    return (
      <PageContainer title="Readiness Score & Evaluation" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <LoadingSpinner text="Computing readiness score and decision rules..." />
      </PageContainer>
    );
  }

  if (error || !data) {
    return (
      <PageContainer title="Readiness Score & Evaluation" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <ErrorMessage title="Unable to Load Readiness Score" message={error} onRetry={refetch} />
      </PageContainer>
    );
  }

  const { employee, readiness, gap_analysis } = data;
  const breakdown = readiness?.breakdown || {};

  // Compute "Why am I not ready?" rationale items
  const whyNotReadyReasons = [];

  if (breakdown.skills?.missing_skills?.length > 0) {
    whyNotReadyReasons.push(
      `Skill Gap: Missing proficiency in ${breakdown.skills.missing_skills.join(', ')} (Score: ${breakdown.skills.score} / ${breakdown.skills.max_score || 40}).`
    );
  }
  if (breakdown.certifications?.missing?.length > 0) {
    whyNotReadyReasons.push(
      `Certification Gap: Unfulfilled certifications: ${breakdown.certifications.missing.join(', ')}.`
    );
  }
  if (breakdown.projects?.remaining > 0) {
    whyNotReadyReasons.push(
      `Project Portfolio: Need ${breakdown.projects.remaining} more completed project(s) (Currently ${breakdown.projects.completed}/${breakdown.projects.required}).`
    );
  }
  if (breakdown.projects?.lead_remaining > 0) {
    whyNotReadyReasons.push(
      `Project Leadership: Need ${breakdown.projects.lead_remaining} more project lead assignment(s).`
    );
  }
  if (breakdown.experience?.gap_years > 0) {
    whyNotReadyReasons.push(
      `Experience Tenure: Need ${breakdown.experience.gap_years} additional year(s) of domain experience.`
    );
  }

  return (
    <PageContainer title="Readiness Score & Evaluation" employeeId={empId} employee={employee} onEmployeeChange={handleEmployeeChange}>
      {/* Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Award className="w-4 h-4" />
            <span>Multi-Factor Readiness Audit</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Promotion Readiness Analysis</h1>
          <p className="text-xs text-slate-400 mt-1">
            Evaluation of readiness score, decision rules, dimensional weightages, and key fulfillment blockers.
          </p>
        </div>
      </div>

      {/* TOP GAUGE & BREAKDOWN CHART */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ReadinessCard readiness={readiness} />
        <div className="lg:col-span-2">
          <ReadinessBreakdownChart breakdown={breakdown} />
        </div>
      </div>

      {/* DETAILED DIMENSION BREAKDOWN TABLE */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Evaluation Dimension Weights & Scores</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] font-bold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Evaluation Dimension</th>
                <th className="py-3 px-4">Weightage</th>
                <th className="py-3 px-4">Achieved Score</th>
                <th className="py-3 px-4">Max Score</th>
                <th className="py-3 px-4">Fulfillment %</th>
                <th className="py-3 px-4">Status / Key Gap</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {/* Skills */}
              {breakdown.skills && (
                <tr>
                  <td className="py-3 px-4 font-semibold text-white">Technical Skills</td>
                  <td className="py-3 px-4">40%</td>
                  <td className="py-3 px-4 font-bold text-indigo-400">{breakdown.skills.score}</td>
                  <td className="py-3 px-4">40</td>
                  <td className="py-3 px-4">{breakdown.skills.percentage}%</td>
                  <td className="py-3 px-4">
                    {breakdown.skills.missing_skills?.length > 0 ? (
                      <span className="text-amber-400 font-medium">Missing: {breakdown.skills.missing_skills.join(', ')}</span>
                    ) : (
                      <Badge variant="emerald">Satisfied</Badge>
                    )}
                  </td>
                </tr>
              )}

              {/* Certifications */}
              {breakdown.certifications && (
                <tr>
                  <td className="py-3 px-4 font-semibold text-white">Certifications</td>
                  <td className="py-3 px-4">15%</td>
                  <td className="py-3 px-4 font-bold text-amber-400">{breakdown.certifications.score}</td>
                  <td className="py-3 px-4">15</td>
                  <td className="py-3 px-4">{((breakdown.certifications.score / 15) * 100).toFixed(0)}%</td>
                  <td className="py-3 px-4">
                    {breakdown.certifications.missing?.length > 0 ? (
                      <span className="text-amber-400 font-medium">Missing: {breakdown.certifications.missing.join(', ')}</span>
                    ) : (
                      <Badge variant="emerald">Satisfied</Badge>
                    )}
                  </td>
                </tr>
              )}

              {/* Experience */}
              {breakdown.experience && (
                <tr>
                  <td className="py-3 px-4 font-semibold text-white">Experience Tenure</td>
                  <td className="py-3 px-4">15%</td>
                  <td className="py-3 px-4 font-bold text-blue-400">{breakdown.experience.score}</td>
                  <td className="py-3 px-4">15</td>
                  <td className="py-3 px-4">{((breakdown.experience.score / 15) * 100).toFixed(0)}%</td>
                  <td className="py-3 px-4">
                    {breakdown.experience.gap_years > 0 ? (
                      <span className="text-amber-400 font-medium">{breakdown.experience.gap_years} yrs remaining</span>
                    ) : (
                      <Badge variant="emerald">Satisfied</Badge>
                    )}
                  </td>
                </tr>
              )}

              {/* Projects */}
              {breakdown.projects && (
                <tr>
                  <td className="py-3 px-4 font-semibold text-white">Project Portfolio</td>
                  <td className="py-3 px-4">20%</td>
                  <td className="py-3 px-4 font-bold text-purple-400">{breakdown.projects.score}</td>
                  <td className="py-3 px-4">20</td>
                  <td className="py-3 px-4">{((breakdown.projects.score / 20) * 100).toFixed(0)}%</td>
                  <td className="py-3 px-4">
                    {breakdown.projects.remaining > 0 ? (
                      <span className="text-amber-400 font-medium">{breakdown.projects.remaining} project(s) left</span>
                    ) : (
                      <Badge variant="emerald">Satisfied</Badge>
                    )}
                  </td>
                </tr>
              )}

              {/* Performance */}
              {breakdown.performance && (
                <tr>
                  <td className="py-3 px-4 font-semibold text-white">Performance Appraisal</td>
                  <td className="py-3 px-4">10%</td>
                  <td className="py-3 px-4 font-bold text-emerald-400">{breakdown.performance.score}</td>
                  <td className="py-3 px-4">10</td>
                  <td className="py-3 px-4">{((breakdown.performance.score / 10) * 100).toFixed(0)}%</td>
                  <td className="py-3 px-4">
                    <Badge variant="emerald">Rating: {breakdown.performance.performance_rating} / 5</Badge>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* WHY AM I NOT READY SECTION */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-2 text-rose-400">
          <HelpCircle className="w-5 h-5" />
          <h3 className="text-base font-bold text-slate-100">Why am I not fully ready for immediate promotion?</h3>
        </div>

        {whyNotReadyReasons.length === 0 ? (
          <div className="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>You meet or exceed all baseline criteria for immediate target grade promotion!</span>
          </div>
        ) : (
          <div className="space-y-3">
            {whyNotReadyReasons.map((reason, idx) => (
              <div key={idx} className="bg-rose-950/20 border border-rose-500/20 p-3.5 rounded-xl flex items-start gap-3 text-xs text-slate-300">
                <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed">{reason}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageContainer>
  );
};

export default Readiness;
