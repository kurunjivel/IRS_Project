import React, { useState } from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Users,
  UserCheck,
  ClipboardCheck,
  History,
  LogOut,
  Menu,
  X,
  Award,
  ShieldCheck,
} from 'lucide-react';

export const ManagerLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'My Direct Reports', path: '/manager', icon: Users },
    { label: 'Calibration & Reviews', path: '/manager/reviews', icon: ClipboardCheck },
    { label: 'Promotion Candidates', path: '/manager/candidates', icon: UserCheck },
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col md:flex-row font-sans">
      {/* Sidebar Desktop */}
      <aside className="hidden md:flex flex-col w-64 bg-slate-800 border-r border-slate-700/60 p-4 space-y-6">
        <div className="flex items-center space-x-3 px-3 py-2 bg-gradient-to-r from-emerald-600/30 to-blue-600/30 rounded-xl border border-emerald-500/30">
          <ShieldCheck className="w-7 h-7 text-emerald-400" />
          <div>
            <div className="font-bold text-slate-100 text-sm tracking-wide">MANAGER PORTAL</div>
            <div className="text-xs text-slate-400">Team Calibration & Reviews</div>
          </div>
        </div>

        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  active
                    ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
                    : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="pt-4 border-t border-slate-700/60">
          <div className="px-3 py-2 text-xs text-slate-400">
            Logged in as <span className="text-emerald-400 font-semibold">{user?.username}</span>
            <span className="block text-slate-500 text-[10px] uppercase">Manager Role</span>
          </div>
          <button
            onClick={handleLogout}
            className="w-full mt-2 flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium text-rose-400 hover:bg-rose-500/10 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Mobile Topbar */}
      <div className="md:hidden flex items-center justify-between p-4 bg-slate-800 border-b border-slate-700">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          <span className="font-bold text-slate-100 text-sm">MANAGER PORTAL</span>
        </div>
        <button onClick={() => setMobileOpen(!mobileOpen)} className="p-2 text-slate-300">
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Navigation Menu */}
      {mobileOpen && (
        <div className="md:hidden bg-slate-800 border-b border-slate-700 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium ${
                  active ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium text-rose-400 hover:bg-rose-500/10"
          >
            <LogOut className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
};
