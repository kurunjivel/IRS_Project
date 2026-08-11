import React from 'react';
import { Menu, Bell, User, ChevronRight, Layers } from 'lucide-react';

export const Header = ({
  title = 'Career Progression Dashboard',
  employee,
  selectedEmpId = 1,
  onEmployeeChange,
  onToggleSidebar,
}) => {
  // Demo employee options (IDs 1 through 5)
  const employeeOptions = [
    { id: 1, name: 'Aarav Sharma (G2 → G3)' },
    { id: 2, name: 'Ananya Iyer (G3 → G4)' },
    { id: 3, name: 'Rohan Verma (G1 → G2)' },
    { id: 4, name: 'Priya Nair (G4 → G5)' },
    { id: 5, name: 'Vikram Patel (G2 → G3)' },
  ];

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/90 border-b border-slate-800 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between">
      {/* Left section: mobile toggle + page title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h2 className="text-lg font-bold text-slate-100 hidden sm:block tracking-tight">{title}</h2>
      </div>

      {/* Right section: Employee Switcher + Target Grade + Avatar */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Employee Switcher Selector */}
        <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700/80 rounded-xl px-3 py-1.5 shadow-inner">
          <Layers className="w-4 h-4 text-indigo-400 hidden sm:block" />
          <select
            value={selectedEmpId}
            onChange={(e) => onEmployeeChange && onEmployeeChange(Number(e.target.value))}
            className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer pr-1"
          >
            {employeeOptions.map((opt) => (
              <option key={opt.id} value={opt.id} className="bg-slate-900 text-slate-200">
                {opt.name}
              </option>
            ))}
          </select>
        </div>

        {/* Grade Transition pill */}
        {employee && (
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1 bg-indigo-500/10 border border-indigo-500/30 rounded-full text-xs font-semibold text-indigo-300">
            <span>{employee.current_grade}</span>
            <ChevronRight className="w-3 h-3 text-indigo-400" />
            <span className="text-indigo-200 font-bold">{employee.target_grade}</span>
          </div>
        )}

        {/* Notifications Icon */}
        <button className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-500 rounded-full"></span>
        </button>

        {/* User Info & Avatar */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold text-xs shadow-md shadow-indigo-600/30">
            {employee?.full_name ? employee.full_name.charAt(0) : <User className="w-4 h-4" />}
          </div>
          <div className="hidden xl:block text-left">
            <p className="text-xs font-semibold text-slate-200 leading-tight">
              {employee?.full_name || 'Aarav Sharma'}
            </p>
            <p className="text-[10px] text-slate-400">{employee?.employee_code || 'EMP001'}</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
