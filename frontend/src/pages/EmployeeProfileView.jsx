import React, { useState, useEffect } from 'react';
import { getMyProfile } from '../api/employeePortalApi';
import { User, Mail, Briefcase, Calendar, Star, Award, Code, CheckCircle } from 'lucide-react';

export const EmployeeProfileView = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyProfile()
      .then(res => setProfile(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading employee profile...</div>;
  }

  if (!profile) {
    return <div className="p-8 text-center text-red-400">Failed to load profile.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100">My Profile</h1>
          <p className="text-xs text-slate-400">Personal information and skill baseline</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center text-2xl font-bold text-white shadow-lg">
            {profile.full_name?.charAt(0)}
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">{profile.full_name}</h2>
            <p className="text-xs text-slate-400">{profile.email} • {profile.employee_code}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-2.5 py-1 bg-indigo-500/20 text-indigo-300 rounded-lg text-xs font-semibold">
                Current: {profile.current_grade}
              </span>
              <span className="px-2.5 py-1 bg-purple-500/20 text-purple-300 rounded-lg text-xs font-semibold">
                Target: {profile.target_grade}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800">
          <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800">
            <p className="text-[11px] font-bold text-slate-400 uppercase">Department</p>
            <p className="text-sm font-semibold text-slate-200 mt-1">{profile.department}</p>
          </div>
          <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800">
            <p className="text-[11px] font-bold text-slate-400 uppercase">Experience</p>
            <p className="text-sm font-semibold text-slate-200 mt-1">{profile.experience_years} Years</p>
          </div>
          <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800">
            <p className="text-[11px] font-bold text-slate-400 uppercase">Performance Rating</p>
            <p className="text-sm font-semibold text-amber-400 mt-1">{profile.performance_rating} / 5.0</p>
          </div>
        </div>

        {/* Skills list */}
        {profile.skills && profile.skills.length > 0 && (
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Current Skills</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {profile.skills.map((s, idx) => (
                <div key={idx} className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-200">{s.skill_name || s.skill}</span>
                  <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] font-bold rounded-md">
                    Level {s.proficiency_level}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeeProfileView;
