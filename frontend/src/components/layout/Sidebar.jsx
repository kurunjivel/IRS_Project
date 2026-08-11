import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  User,
  Target,
  Award,
  Lightbulb,
  TrendingUp,
  BrainCircuit,
  X,
} from 'lucide-react';

export const Sidebar = ({ employeeId = 1, isOpen, onClose }) => {
  const navItems = [
    {
      name: 'Dashboard',
      path: `/dashboard?employee=${employeeId}`,
      icon: LayoutDashboard,
    },
    {
      name: 'My Profile',
      path: `/employee/${employeeId}`,
      icon: User,
    },
    {
      name: 'Gap Analysis',
      path: `/gap-analysis/${employeeId}`,
      icon: Target,
    },
    {
      name: 'Readiness Score',
      path: `/readiness/${employeeId}`,
      icon: Award,
    },
    {
      name: 'Recommendations',
      path: `/recommendations/${employeeId}`,
      icon: Lightbulb,
    },
    {
      name: 'Career Analysis',
      path: `/career-analysis/${employeeId}`,
      icon: TrendingUp,
    },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-slate-900/95 border-r border-slate-800 backdrop-blur-md transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-xl text-white shadow-lg shadow-indigo-600/30">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-slate-100 text-base leading-tight tracking-wide">IRS HR Suite</h1>
              <p className="text-[10px] uppercase font-semibold tracking-wider text-indigo-400">Career Progression</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md shadow-indigo-600/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Footer info */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50">
            <p className="text-xs font-semibold text-slate-300">IRS Recommendation Engine</p>
            <p className="text-[11px] text-slate-500 mt-0.5">FastAPI & ML Powered v1.0</p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
