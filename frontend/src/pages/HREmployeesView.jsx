import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getHREmployees } from '../api/hrApi';
import { Users, Search, ArrowRight, User } from 'lucide-react';

export const HREmployeesView = () => {
  const [employees, setEmployees] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHREmployees()
      .then((res) => setEmployees(res.employees || []))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const filtered = employees.filter((e) =>
    (e.full_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (e.employee_code || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (e.department || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading organization employees...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-100">All Organization Employees</h1>
          <p className="text-xs text-slate-400">Directory of all active workforce members</p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search employee..."
            className="w-full bg-slate-900 border border-slate-800 focus:border-purple-500 rounded-xl py-2 pl-10 pr-4 text-xs text-slate-200 outline-none"
          />
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Code</th>
                <th className="px-6 py-3.5">Employee Name</th>
                <th className="px-6 py-3.5">Department</th>
                <th className="px-6 py-3.5">Current Grade</th>
                <th className="px-6 py-3.5">Target Grade</th>
                <th className="px-6 py-3.5">Experience</th>
                <th className="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((emp) => (
                <tr key={emp.employee_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-6 py-4 font-mono font-semibold text-slate-400">{emp.employee_code}</td>
                  <td className="px-6 py-4 font-bold text-slate-100">{emp.full_name}</td>
                  <td className="px-6 py-4 text-slate-300">{emp.department}</td>
                  <td className="px-6 py-4 font-semibold text-indigo-300">{emp.current_grade}</td>
                  <td className="px-6 py-4 font-semibold text-purple-300">{emp.target_grade}</td>
                  <td className="px-6 py-4 text-slate-300">{emp.experience_years} yrs</td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/hr/employees/${emp.employee_id}`}
                      className="px-3 py-1 bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 rounded-lg font-semibold text-[11px] inline-flex items-center gap-1 transition-colors"
                    >
                      View Report
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default HREmployeesView;
