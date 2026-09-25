import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { managerPortalApi } from '../api/managerPortalApi';
import {
  Users,
  CheckCircle,
  Clock,
  AlertTriangle,
  Award,
  ChevronRight,
  TrendingUp,
  Search,
} from 'lucide-react';

export const ManagerDashboard = () => {
  const navigate = useNavigate();
  const [team, setTeam] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchTeam();
  }, []);

  const fetchTeam = async () => {
    try {
      setLoading(true);
      const res = await managerPortalApi.getManagerTeam();
      setTeam(res.team || []);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to load direct reports team.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center w-fit space-x-1">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>APPROVED (Pool)</span>
          </span>
        );
      case 'REJECTED':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center w-fit space-x-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>REJECTED</span>
          </span>
        );
      case 'NEEDS_DEVELOPMENT':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center w-fit space-x-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>NEEDS DEV</span>
          </span>
        );
      case 'IN_REVIEW':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center w-fit space-x-1">
            <Clock className="w-3.5 h-3.5" />
            <span>IN REVIEW</span>
          </span>
        );
      default:
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-700 text-slate-300 border border-slate-600 flex items-center w-fit space-x-1">
            <Clock className="w-3.5 h-3.5" />
            <span>PENDING</span>
          </span>
        );
    }
  };

  const filteredTeam = team.filter(
    (m) =>
      m.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      m.email?.toLowerCase().includes(search.toLowerCase()) ||
      m.department?.toLowerCase().includes(search.toLowerCase())
  );

  const stats = {
    total: team.length,
    approved: team.filter((m) => m.review_status === 'APPROVED').length,
    pending: team.filter((m) => m.review_status === 'PENDING' || m.review_status === 'IN_REVIEW').length,
    needsDev: team.filter((m) => m.review_status === 'NEEDS_DEVELOPMENT' || m.review_status === 'REJECTED').length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-800/80 p-6 rounded-2xl border border-slate-700/60 shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Users className="w-7 h-7 text-emerald-400" />
            Direct Reports Dashboard & Calibration
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Review IRS readiness scores, SHAP explanations, and submit quarterly manager calibrations.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Total Direct Reports</span>
            <Users className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100 mt-2">{stats.total}</div>
          <p className="text-slate-500 text-xs mt-1">Assigned employees</p>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Pending Calibration</span>
            <Clock className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400 mt-2">{stats.pending}</div>
          <p className="text-slate-500 text-xs mt-1">Awaiting sign-off</p>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">HR Pool Approved</span>
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2">{stats.approved}</div>
          <p className="text-slate-500 text-xs mt-1">Promotable pool active</p>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Needs Development</span>
            <AlertTriangle className="w-5 h-5 text-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400 mt-2">{stats.needsDev}</div>
          <p className="text-slate-500 text-xs mt-1">Feedback / Action plan required</p>
        </div>
      </div>

      {/* Team Table Controls */}
      <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-700/60 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Award className="w-5 h-5 text-emerald-400" />
            Direct Reports Evaluation Roster
          </h2>
          <div className="relative w-full md:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search direct reports..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/60 text-slate-400 text-xs font-semibold uppercase tracking-wider border-b border-slate-700/60">
                <th className="py-3.5 px-6">Employee</th>
                <th className="py-3.5 px-4">Current Grade</th>
                <th className="py-3.5 px-4">Target Grade</th>
                <th className="py-3.5 px-4">Readiness Score</th>
                <th className="py-3.5 px-4">Promo Probability</th>
                <th className="py-3.5 px-4">Calibration Status</th>
                <th className="py-3.5 px-6 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/40 text-sm">
              {filteredTeam.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-8 text-slate-500">
                    No direct reports found.
                  </td>
                </tr>
              ) : (
                filteredTeam.map((member) => (
                  <tr key={member.employee_id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="py-4 px-6 font-medium text-slate-100">
                      <div>{member.full_name}</div>
                      <div className="text-xs text-slate-400">{member.email}</div>
                    </td>
                    <td className="py-4 px-4 text-slate-300">
                      <span className="px-2.5 py-1 bg-slate-700 rounded text-xs">{member.current_grade}</span>
                    </td>
                    <td className="py-4 px-4 text-slate-300">
                      <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-xs font-semibold">
                        {member.target_grade}
                      </span>
                    </td>
                    <td className="py-4 px-4 font-bold text-slate-200">
                      {member.readiness_score?.toFixed(1)} / 100
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="w-4 h-4 text-emerald-400" />
                        <span className="font-semibold text-emerald-400">
                          {(member.promotion_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-4">{getStatusBadge(member.review_status)}</td>
                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={() => navigate(`/manager/employee/${member.employee_id}`)}
                        className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-medium transition-colors inline-flex items-center space-x-1"
                      >
                        <span>Evaluate</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
