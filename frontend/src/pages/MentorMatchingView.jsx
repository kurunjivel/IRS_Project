import React, { useState, useEffect } from 'react';
import { getMyMentors, requestMentorship } from '../api/employeePortalApi';
import { Users, Award, Star, CheckCircle, UserCheck, Sparkles, Send, ShieldCheck, ArrowUpRight } from 'lucide-react';

export const MentorMatchingView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [requestingId, setRequestingId] = useState(null);
  const [requestedMap, setRequestedMap] = useState({});

  useEffect(() => {
    getMyMentors()
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleConnect = async (mentor) => {
    setRequestingId(mentor.mentor_id);
    try {
      await requestMentorship({
        employee_id: data?.employee_id || 1,
        mentor_id: mentor.mentor_id,
        notes: `Interested in mentorship regarding target grade ${data?.target_grade}`,
      });
      setRequestedMap(prev => ({ ...prev, [mentor.mentor_id]: true }));
    } catch (err) {
      console.error(err);
      alert('Could not submit mentorship request. Please try again.');
    } finally {
      setRequestingId(null);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading automated peer & mentor matches...</div>;
  }

  const matches = data?.matches || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            Peer & Mentor Matching Network
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated multi-factor matching for progression from <span className="text-indigo-300 font-semibold">{data?.current_grade}</span> to <span className="text-emerald-300 font-semibold">{data?.target_grade}</span>
          </p>
        </div>
        <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-bold rounded-full self-start sm:self-auto">
          {matches.length} Recommended Match{matches.length !== 1 ? 'es' : ''}
        </span>
      </div>

      {/* Matches Grid */}
      <div className="grid grid-cols-1 gap-6">
        {matches.map((m, idx) => {
          const isPeer = m.match_type === 'PEER_LEARNING_PARTNER';
          const isRequested = requestedMap[m.mentor_id];
          const isRequesting = requestingId === m.mentor_id;

          const matchBadgeBg = m.match_score >= 80 
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
            : m.match_score >= 65
            ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
            : 'bg-amber-500/10 text-amber-400 border-amber-500/20';

          return (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl hover:border-slate-700 transition-all flex flex-col md:flex-row justify-between gap-6">
              
              {/* Left Column: Info & Score */}
              <div className="space-y-4 flex-1">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="text-base font-bold text-white">{m.full_name}</h2>
                      <span className={`px-2.5 py-0.5 text-[10px] font-bold rounded-full border ${isPeer ? 'bg-purple-500/10 text-purple-300 border-purple-500/20' : 'bg-blue-500/10 text-blue-300 border-blue-500/20'}`}>
                        {isPeer ? 'Peer Learning Partner' : 'Senior Mentor'}
                      </span>
                      <span className={`px-2.5 py-0.5 text-[10px] font-bold rounded-full border ${matchBadgeBg}`}>
                        {m.match_level} FIT ({m.match_score.toFixed(0)}%)
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {m.current_grade} • {m.department} • {m.experience_years} Yrs Exp • Rating {m.performance_rating}/5.0
                    </p>
                  </div>
                </div>

                {/* Score Breakdown Bar */}
                <div className="bg-slate-950 p-3.5 rounded-2xl border border-slate-800/80">
                  <p className="text-[11px] font-bold text-slate-300 mb-2">Match Compatibility Breakdown</p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-[10px]">
                    <div className="p-2 bg-slate-900/60 rounded-xl border border-slate-800">
                      <span className="text-slate-400 block">Skill Coverage</span>
                      <span className="font-bold text-indigo-300 text-xs">{m.score_breakdown?.skill_coverage}%</span>
                    </div>
                    <div className="p-2 bg-slate-900/60 rounded-xl border border-slate-800">
                      <span className="text-slate-400 block">Grade & Role</span>
                      <span className="font-bold text-purple-300 text-xs">{m.score_breakdown?.grade_role}%</span>
                    </div>
                    <div className="p-2 bg-slate-900/60 rounded-xl border border-slate-800">
                      <span className="text-slate-400 block">Projects</span>
                      <span className="font-bold text-emerald-300 text-xs">{m.score_breakdown?.project_experience}%</span>
                    </div>
                    <div className="p-2 bg-slate-900/60 rounded-xl border border-slate-800">
                      <span className="text-slate-400 block">Performance</span>
                      <span className="font-bold text-amber-300 text-xs">{m.score_breakdown?.performance_track}%</span>
                    </div>
                  </div>
                </div>

                {/* Covered Skills */}
                {m.covered_gaps && m.covered_gaps.length > 0 && (
                  <div>
                    <p className="text-[11px] font-semibold text-slate-400 mb-1.5 flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                      Skill Gaps Covered ({m.covered_gaps.length}):
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {m.covered_gaps.map((cg, i) => (
                        <span key={i} className="px-2 py-0.5 text-[10px] font-medium bg-slate-950 border border-slate-800 text-slate-300 rounded-lg flex items-center gap-1">
                          <span className="text-indigo-400 font-bold">{cg.required_skill}</span>
                          <span className="text-slate-500">•</span>
                          <span className="text-slate-400">L{cg.mentor_proficiency}</span>
                          {cg.match_type !== 'EXACT_MATCH' && (
                            <span className="text-[9px] text-purple-400 font-bold">({cg.match_type.replace('_', ' ')})</span>
                          )}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Match Reasons */}
                <div className="space-y-1">
                  {m.match_reasons.map((r, i) => (
                    <p key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                      <Sparkles className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                      {r}
                    </p>
                  ))}
                </div>
              </div>

              {/* Right Column: Connect Button */}
              <div className="flex flex-col justify-center items-end border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6">
                {isRequested ? (
                  <button disabled className="w-full md:w-auto px-5 py-2.5 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-xl border border-emerald-500/30 flex items-center justify-center gap-2">
                    <UserCheck className="w-4 h-4" />
                    Request Sent
                  </button>
                ) : (
                  <button
                    onClick={() => handleConnect(m)}
                    disabled={isRequesting}
                    className="w-full md:w-auto px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all shadow-lg hover:shadow-indigo-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <Send className="w-4 h-4" />
                    {isRequesting ? 'Sending Request...' : `Connect with ${isPeer ? 'Peer' : 'Mentor'}`}
                  </button>
                )}
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MentorMatchingView;
