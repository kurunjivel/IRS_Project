import React, { useState } from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  User,
  LineChart,
  Target,
  Lightbulb,
  Map,
  TrendingUp,
  Award,
  LogOut,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';

export const EmployeeLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/employee', icon: LayoutDashboard },
    { label: 'My Profile', path: '/employee/profile', icon: User },
    { label: 'Career Analysis', path: '/employee/career-analysis', icon: LineChart },
    { label: 'Skill Gaps', path: '/employee/skills', icon: Target },
    { label: 'Recommendations', path: '/employee/recommendations', icon: Lightbulb },
    { label: 'Career Roadmap', path: '/employee/roadmap', icon: Map },
    { label: 'My Progress', path: '/employee/progress', icon: TrendingUp },
    { label: 'Promotion Status', path: '/employee/promotion', icon: Award },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col md:flex-row font-sans antialiased">
      {/* Sidebar Navigation */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 transform ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 transition-transform duration-200 ease-in-out flex flex-col justify-between`}
      >
        <div>
          {/* Logo Branding */}
          <div className="h-16 px-6 flex items-center justify-between border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-base text-white tracking-tight">IRS Progression</h1>
                <p className="text-[10px] text-indigo-400 font-semibold uppercase tracking-wider">Employee Portal</p>
              </div>
            </div>
            <button onClick={() => setMobileOpen(false)} className="md:hidden text-slate-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* User Welcome Pill */}
          <div className="px-4 py-4 m-3 bg-slate-800/60 rounded-xl border border-slate-700/50">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-sm text-white shadow">
                {user?.username?.charAt(0).toUpperCase()}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-slate-200 truncate">{user?.username}</p>
                <span className="inline-block px-2 py-0.5 text-[10px] font-bold bg-indigo-500/20 text-indigo-300 rounded-md">
                  Employee
                </span>
              </div>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="px-3 py-2 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    active
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md shadow-indigo-600/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/80'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer Logout */}
        <div className="p-3 border-t border-slate-800">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 md:pl-64 flex flex-col min-h-screen">
        {/* Mobile Header Bar */}
        <header className="h-16 px-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between md:hidden sticky top-0 z-40">
          <div className="flex items-center gap-3">
            <button onClick={() => setMobileOpen(true)} className="p-2 rounded-lg text-slate-400 hover:text-white">
              <Menu className="w-5 h-5" />
            </button>
            <span className="font-bold text-sm text-slate-100">Employee Portal</span>
          </div>
          <button onClick={handleLogout} className="text-xs font-semibold text-red-400 hover:text-red-300">
            Logout
          </button>
        </header>

        {/* Dynamic Page Outlet */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default EmployeeLayout;
