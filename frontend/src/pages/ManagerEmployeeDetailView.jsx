import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { managerPortalApi } from '../api/managerPortalApi';
import {
  ArrowLeft,
  User,
  Award,
  TrendingUp,
  Target,
  CheckCircle,
  AlertTriangle,
  Clock,
  Send,
  History,
  Lightbulb,
  Sliders,
  ShieldCheck,
} from 'lucide-react';

export const ManagerEmployeeDetailView = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();

  const [dossier, setDossier] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  // Calibration Form State
  const [status, setStatus] = useState('APPROVED');
  const [technical, setTechnical] = useState(4);
  const [communication, setCommunication] = useState(4);
  const [leadership, setLeadership] = useState(3);
  const [teamwork, setTeamwork] = useState(4);
  const [ownership, setOwnership] = useState(4);
  const [overallAssessment, setOverallAssessment] = useState('');
  const [comments, setComments] = useState('');

  useEffect(() => {
    fetchDossier();
  }, [employeeId]);

  const fetchDossier = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await managerPortalApi.getEmployeeDossier(employeeId);
      setDossier(data);

      if (data.current_review) {
        const rev = data.current_review;
        setStatus(rev.status || 'APPROVED');
        setTechnical(rev.technical_competency || 4);
        setCommunication(rev.communication || 4);
        setLeadership(rev.leadership || 3);
        setTeamwork(rev.teamwork || 4);
        setOwnership(rev.ownership || 4);
        setOverallAssessment(rev.overall_assessment || '');
        setComments(rev.comments || '');
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to load employee evaluation dossier.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    setSuccessMsg(null);
    setError(null);

    if ((status === 'REJECTED' || status === 'NEEDS_DEVELOPMENT') && !comments.trim()) {
      setError(`Comments are mandatory when review status is '${status}'.`);
      return;
    }

    try {
      setSubmitting(true);
      const res = await managerPortalApi.submitManagerReview({
        employee_id: parseInt(employeeId, 10),
        quarter: 'Q3-2026',
        status,
        technical_competency: technical,
        communication,
        leadership,
        teamwork,
        ownership,
        overall_assessment: overallAssessment,
        comments,
      });

      setSuccessMsg(res.message || 'Calibration review submitted successfully!');
      fetchDossier();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to submit review.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-400"></div>
      </div>
    );
  }

  if (error && !dossier) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <button
          onClick={() => navigate('/manager')}
          className="flex items-center text-slate-400 hover:text-slate-200 text-sm font-medium"
        >
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Direct Reports
        </button>
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-6 rounded-2xl">
          <AlertTriangle className="w-8 h-8 mb-2" />
          <h2 className="text-lg font-bold">Access Denied / Error</h2>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  const emp = dossier.career_analysis.employee;
  const readiness = dossier.career_analysis.readiness;
  const prediction = dossier.career_analysis.prediction;
  const gapAnalysis = dossier.career_analysis.gap_analysis;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/manager')}
        className="flex items-center text-slate-400 hover:text-slate-200 text-sm font-medium transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to Direct Reports Roster
      </button>

      {/* Header Profile Banner */}
      <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 bg-gradient-to-tr from-emerald-500 to-blue-600 rounded-2xl flex items-center justify-center text-white font-extrabold text-2xl shadow-lg">
            {emp.full_name?.charAt(0)}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">{emp.full_name}</h1>
            <div className="text-sm text-slate-400 flex items-center gap-2 mt-0.5">
              <span>{emp.department}</span> • <span>{emp.email}</span>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-2.5 py-1 bg-slate-700 text-slate-300 rounded text-xs">
                Current: {emp.current_grade}
              </span>
              <span className="text-slate-500">→</span>
              <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-xs font-semibold">
                Target: {emp.target_grade}
              </span>
            </div>
          </div>
        </div>

        {/* Readiness & Probability Summary */}
        <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-slate-700/60 pt-4 md:pt-0 md:pl-6">
          <div className="text-center">
            <span className="text-xs text-slate-400 uppercase tracking-wider block">IRS Readiness Score</span>
            <span className="text-3xl font-extrabold text-slate-100">{readiness.readiness_score?.toFixed(1)}</span>
            <span className="text-xs text-slate-500 block">/ 100</span>
          </div>

          <div className="text-center">
            <span className="text-xs text-slate-400 uppercase tracking-wider block">Promo Probability</span>
            <span className="text-3xl font-extrabold text-emerald-400">
              {(prediction.promotion_probability * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-slate-500 block">ML Prediction</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-xl text-sm">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 p-4 rounded-xl text-sm flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <span>{successMsg}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: IRS Analytics & SHAP Explanations */}
        <div className="lg:col-span-2 space-y-6">
          {/* SHAP Impact Analysis */}
          {prediction.shap_analysis && (
            <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl space-y-4">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-amber-400" />
                Explainable AI (SHAP Feature Drivers)
              </h2>
              <p className="text-xs text-slate-400">{prediction.shap_analysis.summary}</p>
              <div className="space-y-2 pt-2">
                {prediction.shap_analysis.factors?.slice(0, 5).map((factor, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center bg-slate-900/60 p-3 rounded-lg text-xs"
                  >
                    <span className="text-slate-300 font-medium">{factor.feature_display}</span>
                    <span
                      className={`font-semibold ${
                        factor.direction === 'POSITIVE' ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {factor.direction === 'POSITIVE' ? '+' : ''}
                      {factor.impact_percentage}% ({factor.shap_value.toFixed(3)})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skill & Certification Gaps */}
          <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl space-y-4">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Target className="w-5 h-5 text-emerald-400" />
              Skill & Certification Gaps
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Skill Gaps ({gapAnalysis.skill_gaps?.length || 0})
                </h3>
                {gapAnalysis.skill_gaps?.length === 0 ? (
                  <p className="text-xs text-emerald-400">All skill requirements met.</p>
                ) : (
                  <div className="space-y-2">
                    {gapAnalysis.skill_gaps?.map((g, i) => (
                      <div key={i} className="bg-slate-900/60 p-2.5 rounded-lg text-xs flex justify-between">
                        <span className="text-slate-300 font-medium">{g.skill}</span>
                        <span className="text-amber-400">Gap: -{g.gap} level(s)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Certification Gaps ({gapAnalysis.certification_gaps?.length || 0})
                </h3>
                {gapAnalysis.certification_gaps?.length === 0 ? (
                  <p className="text-xs text-emerald-400">All required certifications completed.</p>
                ) : (
                  <div className="space-y-2">
                    {gapAnalysis.certification_gaps?.map((c, i) => (
                      <div key={i} className="bg-slate-900/60 p-2.5 rounded-lg text-xs flex justify-between">
                        <span className="text-slate-300 font-medium">{c.certification}</span>
                        <span className="text-rose-400">Missing</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Audit History Log */}
          <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl space-y-4">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <History className="w-5 h-5 text-blue-400" />
              Manager Review Audit Log
            </h2>
            {dossier.audit_history?.length === 0 ? (
              <p className="text-xs text-slate-500">No previous audit entries recorded.</p>
            ) : (
              <div className="space-y-3">
                {dossier.audit_history?.map((log) => (
                  <div key={log.audit_id} className="bg-slate-900/60 p-3 rounded-lg border border-slate-700/40 text-xs space-y-1">
                    <div className="flex justify-between items-center text-slate-400">
                      <span>
                        Status changed: <strong className="text-slate-200">{log.previous_status || 'NONE'}</strong> →{' '}
                        <strong className="text-emerald-400">{log.new_status}</strong>
                      </span>
                      <span>{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                    {log.comments && <p className="text-slate-300 italic">"{log.comments}"</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Quarterly Manager Calibration Form */}
        <div className="space-y-6">
          <form
            onSubmit={handleSubmitReview}
            className="bg-slate-800/90 border border-slate-700/60 p-6 rounded-2xl shadow-2xl space-y-5 sticky top-6"
          >
            <div className="border-b border-slate-700/60 pb-3">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                Quarterly Calibration Form
              </h2>
              <p className="text-xs text-slate-400 mt-1">Submit rating & promotion pool approval decision.</p>
            </div>

            {/* Review Decision Status */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Review Approval Decision
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-100 font-semibold focus:outline-none focus:border-emerald-500"
              >
                <option value="APPROVED">APPROVED (Send to HR Pool)</option>
                <option value="NEEDS_DEVELOPMENT">NEEDS DEVELOPMENT (Action Plan)</option>
                <option value="REJECTED">REJECTED (Hold Promotion)</option>
                <option value="IN_REVIEW">IN REVIEW (Under Calibration)</option>
                <option value="PENDING">PENDING</option>
              </select>
            </div>

            {/* Competency Ratings 1-5 */}
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Competency Ratings (1 to 5)</h3>

              {[
                { label: 'Technical Competency', val: technical, setter: setTechnical },
                { label: 'Communication', val: communication, setter: setCommunication },
                { label: 'Leadership', val: leadership, setter: setLeadership },
                { label: 'Teamwork', val: teamwork, setter: setTeamwork },
                { label: 'Ownership', val: ownership, setter: setOwnership },
              ].map((item, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium text-slate-300">
                    <span>{item.label}</span>
                    <span className="text-emerald-400 font-bold">{item.val} / 5</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    value={item.val}
                    onChange={(e) => item.setter(parseInt(e.target.value, 10))}
                    className="w-full accent-emerald-500"
                  />
                </div>
              ))}
            </div>

            {/* Overall Assessment */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Overall Manager Narrative</label>
              <textarea
                rows="2"
                value={overallAssessment}
                onChange={(e) => setOverallAssessment(e.target.value)}
                placeholder="Key strengths, accomplishments, and team impact..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              ></textarea>
            </div>

            {/* Specific Comments */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Feedback Comments <span className="text-slate-500">(Required for REJECTED / NEEDS DEV)</span>
              </label>
              <textarea
                rows="3"
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="Specific guidance, developmental actions, or rationale..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              ></textarea>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/30 transition-all flex items-center justify-center space-x-2 text-sm disabled:opacity-50"
            >
              {submitting ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Calibration & Review</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
