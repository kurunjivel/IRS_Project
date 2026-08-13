import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getHRAnalytics, getHREmployees, getHRRoles } from '../api/hrApi';
import { Users, Target, ShieldCheck, TrendingUp, ChevronRight, Award, BarChart3 } from 'lucide-react';

export const HRDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getHRAnalytics(), getHREmployees(), getHRRoles()])
      .then(([analyticsRes, empRes, rolesRes]) => {
        setAnalytics(analyticsRes);
        setEmployees(empRes.employees || []);
        setRoles(rolesRes.roles || []);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full text-xs font-semibold text-purple-300 mb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
            HR Administration Dashboard
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Organization Talent Pipeline</h1>
          <p className="text-xs text-slate-400">
            Monitor talent readiness, target grade requirements, and employee progression across your organization.
          </p>
        </div>

        <Link
          to="/hr/roles"
          className="px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-purple-600/30 flex items-center gap-2 transition-all shrink-0"
        >
          <Target className="w-4 h-4" />
          Launch Target Role Analyzer
        </Link>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">Total Active Employees</span>
            <Users className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{analytics?.total_employees || employees.length}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">Available Target Roles</span>
            <Target className="w-5 h-5 text-indigo-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{analytics?.available_roles || roles.length}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">Avg. Performance Rating</span>
            <Award className="w-5 h-5 text-amber-400" />
          </div>
          <p className="text-3xl font-extrabold text-amber-400">{analytics?.average_performance || '4.2'}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">Talent Health</span>
            <TrendingUp className="w-5 h-5 text-emerald-400" />
          </div>
          <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-lg border border-emerald-500/30">
            Strong Pipeline
          </span>
        </div>
      </div>

      {/* Target Roles Quick Action Grid */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Target className="w-4 h-4 text-purple-400" />
          Target Role Fit Engine — Quick Select
        </h2>
        <p className="text-xs text-slate-400">
          Select a target grade below to evaluate all eligible candidates in real time.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
          {roles.map((r) => (
            <Link
              key={r.grade_id}
              to={`/hr/roles?roleId=${r.grade_id}`}
              className="p-4 bg-slate-950/80 border border-slate-800 hover:border-purple-500/50 rounded-2xl transition-all group flex items-center justify-between"
            >
              <div>
                <span className="text-xs font-extrabold text-purple-300 group-hover:text-purple-200">{r.grade_name}</span>
                <p className="text-xs text-slate-400 mt-1">{r.description || `Grade Requirement ${r.grade_id}`}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-purple-400 transition-colors" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HRDashboard;
