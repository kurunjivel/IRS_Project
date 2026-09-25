import React, { useState, useEffect } from 'react';
import { getMyCareerAnalysis, simulateWhatIf } from '../api/employeePortalApi';
import { Sparkles, Sliders, RefreshCw, Award, CheckCircle2, TrendingUp, ShieldCheck, Play } from 'lucide-react';
import Badge from '../components/common/Badge';

export const EmployeeWhatIfSimulator = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState(null);

  // Form state
  const [skillLevels, setSkillLevels] = useState({});
  const [certifications, setCertifications] = useState({});
  const [addProjects, setAddProjects] = useState(0);
  const [addLeadProjects, setAddLeadProjects] = useState(0);
  const [addExperience, setAddExperience] = useState(0);

  useEffect(() => {
    getMyCareerAnalysis()
      .then(res => {
        setAnalysis(res);
        initFormDefaults(res);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const initFormDefaults = (data) => {
    if (!data) return;
    const initialSkills = {};
    const skillsList = data.employee?.skills || data.gap_analysis?.skills || data.gap_analysis?.skill_gaps || [];
    skillsList.forEach(s => {
      const name = s.skill_name || s.skill;
      const level = s.skill_level || s.current_level || 1;
      if (name) initialSkills[name] = level;
    });
    setSkillLevels(initialSkills);

    const initialCerts = {};
    const certsList = data.gap_analysis?.certifications || data.gap_analysis?.certification_gaps || [];
    certsList.forEach(c => {
      const title = c.title || c.certification || c.certification_name;
      if (title) initialCerts[title] = false;
    });
    setCertifications(initialCerts);

    setAddProjects(0);
    setAddLeadProjects(0);
    setAddExperience(0);
    setResult(null);
  };

  const handleSkillChange = (name, val) => {
    setSkillLevels(prev => ({
      ...prev,
      [name]: Math.min(5, Math.max(1, Number(val))),
    }));
  };

  const handleCertToggle = (name) => {
    setCertifications(prev => ({
      ...prev,
      [name]: !prev[name],
    }));
  };

  const handleRunSimulation = async () => {
    if (!analysis?.employee) return;
    setSimulating(true);

    const skillsPayload = Object.entries(skillLevels).map(([skill_name, simulated_level]) => ({
      skill_name,
      simulated_level,
    }));

    const certsPayload = Object.entries(certifications)
      .filter(([_, completed]) => completed)
      .map(([certification_name]) => ({
        certification_name,
        completed: true,
      }));

    const payload = {
      employee_id: analysis.employee.employee_id,
      skills: skillsPayload,
      certifications: certsPayload,
      projects: {
        additional_projects: Number(addProjects) || 0,
        additional_lead_projects: Number(addLeadProjects) || 0,
      },
      experience: {
        additional_experience_years: Number(addExperience) || 0,
      },
    };

    try {
      const res = await simulateWhatIf(payload);
      setResult(res.simulated_readiness_score !== undefined ? res : (res.data || res));
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleReset = () => {
    initFormDefaults(analysis);
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading What-If Scenario Simulator...</div>;
  }

  const emp = analysis?.employee;
  const currentReadiness = analysis?.readiness?.readiness_score || 0;
  const currentProb = (analysis?.prediction?.promotion_probability || 0) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Sliders className="w-4 h-4" />
            <span>Career Advancement Sandbox</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">What-If Scenario Simulator</h1>
          <p className="text-xs text-slate-400 mt-1">
            Experiment with hypothetical skill upgrades, certifications, and experience additions in a zero-risk sandbox.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition flex items-center gap-2 border border-slate-700"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>
          <button
            onClick={handleRunSimulation}
            disabled={simulating}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/30 transition flex items-center gap-2"
          >
            {simulating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            <span>Run Simulation</span>
          </button>
        </div>
      </div>

      {/* Comparison Results Card */}
      {result && (
        <div className="bg-gradient-to-r from-indigo-950/60 via-slate-900 to-purple-950/60 border border-indigo-500/30 rounded-3xl p-6 shadow-2xl space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Simulated vs Baseline Comparison</span>
            </h2>
            <Badge variant="emerald">Simulation Complete</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Readiness Score Diff */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
              <p className="text-xs text-slate-400 font-semibold">Readiness Score</p>
              <div className="flex items-baseline justify-between mt-2">
                <span className="text-slate-400 text-sm">
                  Baseline: <strong className="text-slate-200">{result.baseline_readiness_score}</strong>
                </span>
                <span className="text-3xl font-extrabold text-white">
                  {result.simulated_readiness_score}
                </span>
              </div>
              <div className="mt-3 flex items-center justify-between text-xs pt-3 border-t border-slate-800">
                <span className="text-slate-400">Score Impact</span>
                <span className={`font-bold ${result.readiness_score_diff >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {result.readiness_score_diff >= 0 ? `+${result.readiness_score_diff}` : result.readiness_score_diff} pts
                </span>
              </div>
            </div>

            {/* Promotion Probability Diff */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
              <p className="text-xs text-slate-400 font-semibold">Promotion Probability</p>
              <div className="flex items-baseline justify-between mt-2">
                <span className="text-slate-400 text-sm">
                  Baseline: <strong className="text-slate-200">{(result.baseline_promotion_probability * 100).toFixed(1)}%</strong>
                </span>
                <span className="text-3xl font-extrabold text-indigo-300">
                  {(result.simulated_promotion_probability * 100).toFixed(1)}%
                </span>
              </div>
              <div className="mt-3 flex items-center justify-between text-xs pt-3 border-t border-slate-800">
                <span className="text-slate-400">Probability Impact</span>
                <span className={`font-bold ${result.probability_diff >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {result.probability_diff >= 0 ? `+${(result.probability_diff * 100).toFixed(1)}%` : `${(result.probability_diff * 100).toFixed(1)}%`}
                </span>
              </div>
            </div>
          </div>

          {/* Resolved Gaps */}
          {(result.resolved_skill_gaps?.length > 0 || result.resolved_certifications?.length > 0) && (
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase">Newly Satisfied Requirements</h3>
              <div className="flex flex-wrap gap-2">
                {result.resolved_skill_gaps?.map((s, idx) => (
                  <span key={`s-${idx}`} className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Skill: {s}</span>
                  </span>
                ))}
                {result.resolved_certifications?.map((c, idx) => (
                  <span key={`c-${idx}`} className="px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full text-xs font-semibold flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5" />
                    <span>Cert: {c}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.simulated_shap_summary && (
            <p className="text-xs text-slate-400 italic bg-slate-950 p-3 rounded-xl border border-slate-800">
              "{result.simulated_shap_summary}"
            </p>
          )}
        </div>
      )}

      {/* Simulator Inputs Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skill Level Sliders */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>1. Simulate Skill Levels (1 - 5)</span>
          </h2>

          <div className="space-y-4">
            {Object.entries(skillLevels).map(([skill_name, level], idx) => (
              <div key={idx} className="space-y-1.5 bg-slate-950 p-3.5 rounded-2xl border border-slate-800">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-200">{skill_name}</span>
                  <span className="font-bold text-indigo-400">Level {level} / 5</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="1"
                  value={level}
                  onChange={(e) => handleSkillChange(skill_name, e.target.value)}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Certifications & Experience Toggles */}
        <div className="space-y-6">
          {/* Certification Toggles */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Award className="w-4 h-4 text-indigo-400" />
              <span>2. Simulate Certification Completions</span>
            </h2>

            {analysis?.gap_analysis?.certifications?.length > 0 ? (
              <div className="space-y-2">
                {analysis.gap_analysis.certifications.map((c, idx) => (
                  <label key={idx} className="flex items-center justify-between p-3.5 bg-slate-950 rounded-2xl border border-slate-800 cursor-pointer hover:border-slate-700 transition">
                    <span className="text-xs font-semibold text-slate-200">{c.title}</span>
                    <input
                      type="checkbox"
                      checked={!!certifications[c.title]}
                      onChange={() => handleCertToggle(c.title)}
                      className="w-4 h-4 rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-indigo-500 accent-indigo-500"
                    />
                  </label>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">All required target certifications are currently satisfied.</p>
            )}
          </div>

          {/* Experience & Projects Additions */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span>3. Project & Tenure Experience</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-[11px] font-semibold text-slate-400 block mb-1">Add Projects</label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={addProjects}
                  onChange={(e) => setAddProjects(Math.min(10, Math.max(0, Number(e.target.value))))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-400 block mb-1">Add Lead Roles</label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  value={addLeadProjects}
                  onChange={(e) => setAddLeadProjects(Math.min(5, Math.max(0, Number(e.target.value))))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-400 block mb-1">Add Experience (Yrs)</label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  step="0.5"
                  value={addExperience}
                  onChange={(e) => setAddExperience(Math.min(10, Math.max(0, Number(e.target.value))))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-indigo-500 outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeWhatIfSimulator;
