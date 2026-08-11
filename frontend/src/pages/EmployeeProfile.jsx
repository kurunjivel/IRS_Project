import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PageContainer from '../components/layout/PageContainer';
import { useEmployee } from '../hooks/useEmployee';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Badge from '../components/common/Badge';
import {
  User,
  Mail,
  Building,
  Clock,
  Star,
  Calendar,
  Award,
  Code,
  Briefcase,
  ChevronRight,
} from 'lucide-react';

export const EmployeeProfile = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const empId = Number(employeeId) || 1;

  const { employee, loading, error } = useEmployee(empId);

  const handleEmployeeChange = (newId) => {
    navigate(`/employee/${newId}`);
  };

  if (loading) {
    return (
      <PageContainer title="Employee Profile" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <LoadingSpinner text="Loading employee profile details..." />
      </PageContainer>
    );
  }

  if (error || !employee) {
    return (
      <PageContainer title="Employee Profile" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <ErrorMessage title="Profile Load Failure" message={error || 'Employee record not found.'} />
      </PageContainer>
    );
  }

  const skills = employee.skills || [];
  const certs = employee.certifications || [];
  const projects = employee.projects || [];

  return (
    <PageContainer title="Employee Profile" employeeId={empId} employee={employee} onEmployeeChange={handleEmployeeChange}>
      {/* Profile Overview Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-extrabold text-3xl shadow-lg shadow-indigo-600/30">
            {employee.full_name?.charAt(0) || <User className="w-8 h-8" />}
          </div>
          <div>
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <h1 className="text-2xl font-bold text-white tracking-tight">{employee.full_name}</h1>
              <Badge variant="indigo">{employee.employee_code}</Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center justify-center sm:justify-start gap-2">
              <Building className="w-3.5 h-3.5 text-indigo-400" />
              <span>{employee.department}</span>
              <span>•</span>
              <Mail className="w-3.5 h-3.5 text-indigo-400" />
              <span>{employee.email}</span>
            </p>
          </div>
        </div>

        {/* Grade Indicator Pill */}
        <div className="bg-slate-950/80 border border-slate-800 px-5 py-3 rounded-xl flex items-center gap-4 shadow-inner">
          <div>
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Current Grade</span>
            <span className="text-xl font-black text-slate-200">{employee.current_grade}</span>
          </div>
          <ChevronRight className="w-5 h-5 text-indigo-400" />
          <div>
            <span className="text-[10px] text-indigo-400 uppercase font-bold block">Target Grade</span>
            <span className="text-xl font-black text-indigo-300">{employee.target_grade}</span>
          </div>
        </div>
      </div>

      {/* Profile Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Clock className="w-5 h-5 text-indigo-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Total Experience</p>
            <p className="text-base font-bold text-slate-100">{employee.experience_years} years</p>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Star className="w-5 h-5 text-amber-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Performance Rating</p>
            <p className="text-base font-bold text-slate-100">{employee.performance_rating} / 5.0</p>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Calendar className="w-5 h-5 text-emerald-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Joining Date</p>
            <p className="text-base font-bold text-slate-100">{employee.joining_date || 'N/A'}</p>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-md flex items-center gap-3">
          <Briefcase className="w-5 h-5 text-purple-400" />
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-semibold">Completed Projects</p>
            <p className="text-base font-bold text-slate-100">{projects.length} projects</p>
          </div>
        </div>
      </div>

      {/* SKILLS TABLE */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5">
          <Code className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-slate-100">Current Technical & Domain Skills</h3>
        </div>

        {skills.length === 0 ? (
          <p className="text-xs text-slate-500">No skills logged in employee record.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {skills.map((s, idx) => (
              <div key={idx} className="bg-slate-950/60 border border-slate-800 p-3.5 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-sm font-bold text-slate-200">{s.skill_name || s.skill}</p>
                  <p className="text-xs text-slate-400">{s.category || 'General'}</p>
                </div>
                <span className="px-2.5 py-1 bg-indigo-500/20 text-indigo-300 font-bold text-xs rounded-lg border border-indigo-500/30">
                  Lvl {s.proficiency_level ?? s.level}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* CERTIFICATIONS TABLE */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5">
          <Award className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-bold text-slate-100">Active Certifications</h3>
        </div>

        {certs.length === 0 ? (
          <p className="text-xs text-slate-500">No active certifications recorded.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {certs.map((c, idx) => (
              <div key={idx} className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-200">{c.certification_name || c.name}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">Provider: {c.provider} • Issued: {c.issue_date || 'N/A'}</p>
                </div>
                <Badge variant="emerald">Completed</Badge>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* PROJECTS TABLE */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-2.5">
          <Briefcase className="w-5 h-5 text-purple-400" />
          <h3 className="text-base font-bold text-slate-100">Completed Project Portfolio</h3>
        </div>

        {projects.length === 0 ? (
          <p className="text-xs text-slate-500">No completed projects on record.</p>
        ) : (
          <div className="space-y-3">
            {projects.map((p, idx) => (
              <div key={idx} className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-slate-200">{p.project_name || p.name}</h4>
                    {p.is_lead && <Badge variant="amber">Lead Role</Badge>}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Tech: <span className="text-slate-300 font-mono">{p.technology_used || p.technology}</span></p>
                </div>
                <div className="text-right text-xs text-slate-400">
                  <p>Role: <strong className="text-slate-200">{p.role || 'Contributor'}</strong></p>
                  <p>Duration: {p.duration_months} months • Rating: <span className="text-amber-400 font-bold">{p.rating} / 5</span></p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageContainer>
  );
};

export default EmployeeProfile;
