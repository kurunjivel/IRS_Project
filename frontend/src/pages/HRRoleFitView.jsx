import React, { useState, useEffect } from 'react';
import { getHRRoles, getRoleCandidates, getHREmployeePromotionStatus } from '../api/hrApi';
import {
  Target,
  Users,
  Award,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  Filter,
  SlidersHorizontal,
  Search,
  Sparkles,
} from 'lucide-react';

export const HRRoleFitView = () => {
  const [roles, setRoles] = useState([]);
  const [selectedRoleId, setSelectedRoleId] = useState('');
  const [candidatesData, setCandidatesData] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [candidatePromoStatus, setCandidatePromoStatus] = useState(null);
  const [loadingRoles, setLoadingRoles] = useState(true);
  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [error, setError] = useState(null);

  // Fetch available target roles
  useEffect(() => {
    getHRRoles()
      .then((res) => {
        const list = res.roles || [];
        setRoles(list);
        if (list.length > 0) {
          // Default to G3 or first grade
          const defaultRole = list.find((r) => r.grade_name === 'G3') || list[0];
          setSelectedRoleId(defaultRole.grade_id);
        }
      })
      .catch((err) => {
        console.error('Failed to load roles:', err);
        setError('Failed to fetch available target roles/grades.');
      })
      .finally(() => setLoadingRoles(false));
  }, []);

  // Fetch candidates whenever target role changes
  useEffect(() => {
    if (!selectedRoleId) return;
    setLoadingCandidates(true);
    setSelectedCandidate(null);
    setCandidatePromoStatus(null);
    getRoleCandidates(selectedRoleId)
      .then((res) => setCandidatesData(res))
      .catch((err) => {
        console.error('Failed to load candidates for role:', err);
        setError('Failed to analyze candidates for selected role.');
      })
      .finally(() => setLoadingCandidates(false));
  }, [selectedRoleId]);

  const handleSelectCandidate = async (candidate) => {
    setSelectedCandidate(candidate);
    try {
      const statusRes = await getHREmployeePromotionStatus(candidate.employee_id);
      setCandidatePromoStatus(statusRes);
    } catch (err) {
      console.error('Failed to fetch candidate promotion status:', err);
    }
  };

  if (loadingRoles) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-500" />
      </div>
    );
  }

  const candidates = candidatesData?.candidates || [];

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full text-xs font-semibold text-purple-300 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            Target Role Fit Engine
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">HR Candidate Fit & Ranking</h1>
          <p className="text-xs text-slate-400">
            Select a target role/grade to analyze and rank candidate suitability across your organization.
          </p>
        </div>

        {/* Target Role Selector */}
        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 p-3 rounded-2xl shadow-lg">
          <Target className="w-5 h-5 text-purple-400 shrink-0" />
          <div className="flex flex-col">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Select Target Role / Grade</label>
            <select
              value={selectedRoleId}
              onChange={(e) => setSelectedRoleId(Number(e.target.value))}
              className="bg-transparent text-sm font-bold text-white focus:outline-none cursor-pointer pr-4"
            >
              {roles.map((r) => (
                <option key={r.grade_id} value={r.grade_id} className="bg-slate-900 text-slate-200">
                  {r.grade_name} — {r.description || `Grade ${r.grade_id}`}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Target Role Overview Banner */}
      {candidatesData && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              Target Role: <span className="text-purple-400">{candidatesData.target_role_name}</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {candidatesData.description || 'Target grade requirement evaluation across active talent.'}
            </p>
          </div>

          <div className="flex items-center gap-4 text-center">
            <div className="px-4 py-2 bg-slate-950/80 border border-slate-800 rounded-2xl">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Total Candidates</p>
              <p className="text-xl font-extrabold text-white">{candidatesData.total_candidates}</p>
            </div>
            <div className="px-4 py-2 bg-slate-950/80 border border-slate-800 rounded-2xl">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Top Fit Score</p>
              <p className="text-xl font-extrabold text-emerald-400">
                {candidates.length > 0 ? `${candidates[0].role_fit_score}%` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Candidate Ranking Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Users className="w-4 h-4 text-purple-400" />
            Candidate Ranking List (Sorted by Role Fit Score)
          </h3>
          <span className="text-xs text-slate-400 font-medium">
            {loadingCandidates ? 'Calculating fit scores...' : `${candidates.length} candidates evaluated`}
          </span>
        </div>

        {loadingCandidates ? (
          <div className="p-12 text-center text-slate-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-3" />
            Analyzing candidates against selected target grade...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3.5">Rank</th>
                  <th className="px-6 py-3.5">Candidate Name</th>
                  <th className="px-6 py-3.5">Current Grade</th>
                  <th className="px-6 py-3.5">Role Fit Score</th>
                  <th className="px-6 py-3.5">Readiness Score</th>
                  <th className="px-6 py-3.5">Promotion Prob.</th>
                  <th className="px-6 py-3.5">Eligibility</th>
                  <th className="px-6 py-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {candidates.map((cand, idx) => (
                  <tr
                    key={cand.employee_id}
                    onClick={() => handleSelectCandidate(cand)}
                    className={`hover:bg-slate-800/50 cursor-pointer transition-colors ${
                      selectedCandidate?.employee_id === cand.employee_id ? 'bg-purple-950/30 border-l-4 border-purple-500' : ''
                    }`}
                  >
                    <td className="px-6 py-4 font-extrabold text-slate-400">
                      #{idx + 1}
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-100">
                      {cand.name}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-300">
                      <span className="px-2.5 py-1 bg-slate-800 border border-slate-700 rounded-md font-semibold text-slate-200">
                        {cand.current_grade}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-extrabold text-purple-400">
                      <div className="flex items-center gap-2">
                        <span>{cand.role_fit_score}%</span>
                        <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden hidden sm:block">
                          <div
                            className="bg-purple-500 h-full rounded-full"
                            style={{ width: `${cand.role_fit_score}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-extrabold text-indigo-300">
                      {cand.readiness_score.toFixed(1)} / 100
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-300">
                      {(cand.promotion_probability * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-md font-bold text-[11px] ${
                          cand.eligibility === 'Eligible'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : cand.eligibility === 'Conditional'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-red-500/20 text-red-300 border border-red-500/30'
                        }`}
                      >
                        {cand.eligibility}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="px-3 py-1 bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 rounded-lg font-semibold text-[11px] transition-colors">
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Selected Candidate Detailed Inspection Card */}
      {selectedCandidate && (
        <div className="bg-slate-900 border border-purple-500/30 rounded-3xl p-6 shadow-2xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <div className="inline-block px-2.5 py-0.5 bg-purple-500/20 text-purple-300 text-[10px] font-bold rounded-md mb-1">
                Candidate Deep Dive (HR Perspective)
              </div>
              <h3 className="text-lg font-bold text-white">{selectedCandidate.name}</h3>
              <p className="text-xs text-slate-400">
                Transition: {selectedCandidate.current_grade} → {selectedCandidate.target_grade}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-center px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl">
                <p className="text-[10px] font-bold text-slate-400 uppercase">Role Fit</p>
                <p className="text-base font-extrabold text-purple-400">{selectedCandidate.role_fit_score}%</p>
              </div>
              <div className="text-center px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl">
                <p className="text-[10px] font-bold text-slate-400 uppercase">Readiness</p>
                <p className="text-base font-extrabold text-indigo-300">{selectedCandidate.readiness_score.toFixed(1)}</p>
              </div>
            </div>
          </div>

          {/* Role Fit Breakdown Bars */}
          {selectedCandidate.breakdown && (
            <div>
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Fit Component Breakdown</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {Object.entries(selectedCandidate.breakdown).map(([key, val]) => (
                  <div key={key} className="p-3 bg-slate-950 border border-slate-800 rounded-xl">
                    <p className="text-[10px] font-bold text-slate-400 capitalize">{key.replace('_', ' ')}</p>
                    <p className="text-sm font-extrabold text-white mt-1">{val}%</p>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div className="bg-purple-500 h-full rounded-full" style={{ width: `${val}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Third Person HR Promotion Status Callout */}
          {candidatePromoStatus && (
            <div className="p-5 bg-slate-950 border border-slate-800 rounded-2xl space-y-3">
              <div className="flex items-start gap-3">
                {candidatePromoStatus.is_eligible ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                )}
                <div>
                  <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">{candidatePromoStatus.status_title}</h4>
                  <p className="text-sm font-bold text-white mt-1">{candidatePromoStatus.headline}</p>
                </div>
              </div>

              {candidatePromoStatus.reasons && candidatePromoStatus.reasons.length > 0 && (
                <div className="pt-3 border-t border-slate-800">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{candidatePromoStatus.gap_headline}</p>
                  <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                    {candidatePromoStatus.reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HRRoleFitView;
