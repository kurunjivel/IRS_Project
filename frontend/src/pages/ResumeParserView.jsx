import React, { useState } from 'react';
import api from '../api/axios';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, ArrowRight, ShieldCheck, Sparkles, RefreshCw, Layers } from 'lucide-react';

export const ResumeParserView = () => {
  const [file, setFile] = useState(null);
  const [parsing, setParsing] = useState(false);
  const [parseResult, setParseResult] = useState(null);
  const [error, setError] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const [confirmedSuccess, setConfirmedSuccess] = useState(null);

  // Candidate selection states
  const [selectedNewSkills, setSelectedNewSkills] = useState({});
  const [selectedUpgrades, setSelectedUpgrades] = useState({});
  const [selectedCerts, setSelectedCerts] = useState({});
  const [selectedProjects, setSelectedProjects] = useState({});

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setParseResult(null);
      setConfirmedSuccess(null);
    }
  };

  const handleUploadAndParse = async () => {
    if (!file) return;
    setParsing(true);
    setError(null);
    setParseResult(null);
    setConfirmedSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/employee/me/resume/parse', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setParseResult(res.data);

      // Pre-select all candidate items by default
      const changes = res.data.candidate_changes || {};
      const newSkMap = {};
      (changes.new_skills || []).forEach((sk, i) => { newSkMap[i] = true; });
      setSelectedNewSkills(newSkMap);

      const upgMap = {};
      (changes.upgraded_skills || []).forEach((sk, i) => { upgMap[i] = true; });
      setSelectedUpgrades(upgMap);

      const certMap = {};
      (changes.new_certifications || []).forEach((c, i) => { certMap[i] = true; });
      setSelectedCerts(certMap);

      const projMap = {};
      (changes.new_projects || []).forEach((p, i) => { projMap[i] = true; });
      setSelectedProjects(projMap);
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.detail || 'Failed to extract resume text. Please check the file format.';
      setError(msg);
    } finally {
      setParsing(false);
    }
  };

  const handleConfirmUpdates = async () => {
    if (!parseResult) return;
    setConfirming(true);
    const changes = parseResult.candidate_changes || {};

    const confirmedSkills = [
      ...(changes.new_skills || []).filter((_, i) => selectedNewSkills[i]),
      ...(changes.upgraded_skills || []).filter((_, i) => selectedUpgrades[i]),
    ];
    const confirmedCerts = (changes.new_certifications || []).filter((_, i) => selectedCerts[i]);
    const confirmedProjects = (changes.new_projects || []).filter((_, i) => selectedProjects[i]);

    try {
      const res = await api.post('/employee/me/resume/confirm', {
        confirmed_skills: confirmedSkills,
        confirmed_certifications: confirmedCerts,
        confirmed_projects: confirmedProjects,
      });
      setConfirmedSuccess(res.data);
      setParseResult(null);
    } catch (err) {
      console.error(err);
      alert('Could not update profile. Please try again.');
    } finally {
      setConfirming(false);
    }
  };

  const changes = parseResult?.candidate_changes || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            Resume/CV Intelligent Profile Extraction
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Upload your latest resume (PDF/DOCX/TXT) to extract skills, certifications, and projects for your explicit confirmation.
          </p>
        </div>
      </div>

      {/* File Upload Box */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
        <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-2xl p-8 text-center transition-all bg-slate-950/40">
          <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-200">
            {file ? file.name : 'Select or drag your Resume/CV file'}
          </p>
          <p className="text-xs text-slate-500 mt-1">Supported formats: PDF, DOCX, TXT (Text-based)</p>
          
          <input
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleFileChange}
            className="hidden"
            id="resume-upload-input"
          />
          <div className="mt-4 flex justify-center gap-3">
            <label
              htmlFor="resume-upload-input"
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl cursor-pointer transition-all"
            >
              Browse File
            </label>
            {file && (
              <button
                onClick={handleUploadAndParse}
                disabled={parsing}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all shadow-lg flex items-center gap-2 disabled:opacity-50"
              >
                {parsing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Extracting NLP Data...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Extract & Compare Profile
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-xs text-red-300 flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Confirmed Success Banner */}
      {confirmedSuccess && (
        <div className="bg-slate-900 border border-emerald-500/30 rounded-3xl p-6 shadow-xl space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Profile Successfully Updated!</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Applied {confirmedSuccess.applied_updates?.skills_added_or_upgraded} skill(s), {confirmedSuccess.applied_updates?.certifications_added} certification(s), and {confirmedSuccess.applied_updates?.projects_added} project(s) to your verified profile.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Extracted Candidate Review & Confirmation Panel */}
      {parseResult && (
        <div className="bg-slate-900 border border-indigo-500/30 rounded-3xl p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                Candidate Changes Review & Confirmation
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Review extracted items below. Check items you wish to explicitly confirm for database profile update.
              </p>
            </div>
            <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-bold rounded-full">
              {changes.total_candidate_updates || 0} Candidate Update(s) Detected
            </span>
          </div>

          {/* New Skills */}
          {changes.new_skills && changes.new_skills.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">New Skills Detected ({changes.new_skills.length})</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {changes.new_skills.map((sk, idx) => (
                  <label key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-between cursor-pointer hover:border-slate-700 transition-all">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={!!selectedNewSkills[idx]}
                        onChange={(e) => setSelectedNewSkills(prev => ({ ...prev, [idx]: e.target.checked }))}
                        className="w-4 h-4 accent-indigo-600 rounded"
                      />
                      <div>
                        <p className="text-xs font-bold text-slate-200">{sk.skill_name}</p>
                        <p className="text-[10px] text-slate-400">{sk.category} • Suggested Level {sk.suggested_level}</p>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md">New Skill</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Upgraded Skills */}
          {changes.upgraded_skills && changes.upgraded_skills.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Skill Level Upgrades ({changes.upgraded_skills.length})</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {changes.upgraded_skills.map((sk, idx) => (
                  <label key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-between cursor-pointer hover:border-slate-700 transition-all">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={!!selectedUpgrades[idx]}
                        onChange={(e) => setSelectedUpgrades(prev => ({ ...prev, [idx]: e.target.checked }))}
                        className="w-4 h-4 accent-indigo-600 rounded"
                      />
                      <div>
                        <p className="text-xs font-bold text-slate-200">{sk.skill_name}</p>
                        <p className="text-[10px] text-slate-400">Current Level {sk.current_level} → Suggested Level {sk.suggested_level}</p>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-md">Level Upgrade</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* New Certifications */}
          {changes.new_certifications && changes.new_certifications.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">New Certifications ({changes.new_certifications.length})</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {changes.new_certifications.map((c, idx) => (
                  <label key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-between cursor-pointer hover:border-slate-700 transition-all">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={!!selectedCerts[idx]}
                        onChange={(e) => setSelectedCerts(prev => ({ ...prev, [idx]: e.target.checked }))}
                        className="w-4 h-4 accent-indigo-600 rounded"
                      />
                      <div>
                        <p className="text-xs font-bold text-slate-200">{c.certification_name}</p>
                        <p className="text-[10px] text-slate-400">Status: {c.status}</p>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-md">New Certification</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* New Projects */}
          {changes.new_projects && changes.new_projects.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">New Projects ({changes.new_projects.length})</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {changes.new_projects.map((p, idx) => (
                  <label key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-between cursor-pointer hover:border-slate-700 transition-all">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={!!selectedProjects[idx]}
                        onChange={(e) => setSelectedProjects(prev => ({ ...prev, [idx]: e.target.checked }))}
                        className="w-4 h-4 accent-indigo-600 rounded"
                      />
                      <div>
                        <p className="text-xs font-bold text-slate-200">{p.project_name}</p>
                        <p className="text-[10px] text-slate-400">{p.role_description}</p>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-md">New Project</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Action Confirmation Button */}
          <div className="pt-4 border-t border-slate-800 flex justify-end">
            <button
              onClick={handleConfirmUpdates}
              disabled={confirming}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition-all shadow-lg flex items-center gap-2 disabled:opacity-50"
            >
              {confirming ? 'Updating Profile...' : 'Confirm & Update Profile'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeParserView;
