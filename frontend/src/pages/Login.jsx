import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  UserCheck,
  Lock,
  User,
  ArrowRight,
  Sparkles,
  AlertCircle,
  UserPlus,
  LogIn,
  CheckCircle2,
  BadgeCheck,
  Building2,
} from 'lucide-react';

export const Login = () => {
  const [activeTab, setActiveTab] = useState('login'); // 'login' or 'register'

  // Login Form state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState('EMPLOYEE');
  const [submitting, setSubmitting] = useState(false);
  const [loginError, setLoginError] = useState('');

  // New User Registration Form state
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [regRole, setRegRole] = useState('EMPLOYEE');
  const [regEmployeeId, setRegEmployeeId] = useState('1');
  const [regSubmitting, setRegSubmitting] = useState(false);
  const [regError, setRegError] = useState('');
  const [regSuccess, setRegSuccess] = useState('');

  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Quick fill demo credentials for existing users
  const handleQuickFill = (role) => {
    setActiveTab('login');
    if (role === 'HR') {
      setUsername('hr');
      setPassword('hr123');
      setSelectedRole('HR');
    } else {
      setUsername('aarav');
      setPassword('password123');
      setSelectedRole('EMPLOYEE');
    }
  };

  // Quick preset for New User creation
  const handleNewUserPreset = (roleType) => {
    setActiveTab('register');
    const randomNum = Math.floor(100 + Math.random() * 900);
    setRegRole(roleType);
    if (roleType === 'HR') {
      setRegUsername(`hr_manager_${randomNum}`);
      setRegPassword('hrpass123');
      setRegConfirmPassword('hrpass123');
    } else {
      setRegUsername(`employee_${randomNum}`);
      setRegPassword('emppass123');
      setRegConfirmPassword('emppass123');
      setRegEmployeeId('1');
    }
    setRegError('');
  };

  // Handle Login Submit
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setLoginError('Please enter both username and password.');
      return;
    }

    setSubmitting(true);
    setLoginError('');

    try {
      const userPayload = await login(username, password);
      const from = location.state?.from?.pathname;

      if (userPayload.role === 'HR') {
        navigate(from && from.startsWith('/hr') ? from : '/hr');
      } else {
        navigate(from && from.startsWith('/employee') ? from : '/employee');
      }
    } catch (err) {
      setLoginError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle New User Registration Submit
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setRegError('');
    setRegSuccess('');

    if (!regUsername || !regPassword || !regConfirmPassword) {
      setRegError('Please complete all required registration fields.');
      return;
    }

    if (regUsername.trim().length < 3) {
      setRegError('Username must be at least 3 characters long.');
      return;
    }

    if (regPassword.length < 4) {
      setRegError('Password must be at least 4 characters long.');
      return;
    }

    if (regPassword !== regConfirmPassword) {
      setRegError('Passwords do not match. Please re-enter.');
      return;
    }

    setRegSubmitting(true);

    try {
      const empId = regRole === 'EMPLOYEE' ? parseInt(regEmployeeId, 10) || 1 : null;
      const userPayload = await register(regUsername, regPassword, regRole, empId);
      
      setRegSuccess(`Account "${userPayload.username}" created successfully! Redirecting...`);

      setTimeout(() => {
        const from = location.state?.from?.pathname;
        if (userPayload.role === 'HR') {
          navigate(from && from.startsWith('/hr') ? from : '/hr');
        } else {
          navigate(from && from.startsWith('/employee') ? from : '/employee');
        }
      }, 1000);
    } catch (err) {
      setRegError(err.message || 'Registration failed. Username may already be in use.');
    } finally {
      setRegSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 relative overflow-hidden font-sans">
      {/* Dynamic Background Glows */}
      <div className="absolute top-1/4 -left-20 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />

      {/* Main Container Card */}
      <div className="w-full max-w-md bg-slate-900/90 border border-slate-800 rounded-3xl p-8 shadow-2xl backdrop-blur-xl z-10 transition-all duration-300">
        {/* Header Branding */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 bg-gradient-to-tr from-indigo-500 via-purple-500 to-emerald-400 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/30">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Intelligent Recommendation System</h1>
          <p className="text-xs text-slate-400 mt-1">Internal Career Progression Platform</p>
        </div>

        {/* Tab Switcher: Login vs New User Registration */}
        <div className="flex bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800/80 mb-6">
          <button
            type="button"
            onClick={() => setActiveTab('login')}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'login'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md shadow-indigo-600/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
            }`}
          >
            <LogIn className="w-4 h-4" />
            Existing Login
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('register')}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'register'
                ? 'bg-gradient-to-r from-emerald-600 to-indigo-600 text-white shadow-md shadow-emerald-600/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
            }`}
          >
            <UserPlus className="w-4 h-4" />
            New User Signup
          </button>
        </div>

        {/* Quick Demo Credentials Bar */}
        <div className="mb-6 p-3 bg-slate-800/40 border border-slate-700/50 rounded-2xl">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 text-center flex items-center justify-center gap-1.5">
            <BadgeCheck className="w-3.5 h-3.5 text-indigo-400" />
            {activeTab === 'login' ? 'Quick Demo Login Fill' : 'Quick New User Generator'}
          </p>
          <div className="grid grid-cols-2 gap-2">
            {activeTab === 'login' ? (
              <>
                <button
                  type="button"
                  onClick={() => handleQuickFill('EMPLOYEE')}
                  className={`flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-[11px] font-semibold transition-all ${
                    selectedRole === 'EMPLOYEE'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  <UserCheck className="w-3.5 h-3.5" />
                  Employee (aarav)
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('HR')}
                  className={`flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-[11px] font-semibold transition-all ${
                    selectedRole === 'HR'
                      ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  HR Admin (hr)
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => handleNewUserPreset('EMPLOYEE')}
                  className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-[11px] font-semibold bg-emerald-600/80 hover:bg-emerald-600 text-white transition-all shadow-md shadow-emerald-600/20"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  Auto-Gen Employee
                </button>
                <button
                  type="button"
                  onClick={() => handleNewUserPreset('HR')}
                  className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-[11px] font-semibold bg-indigo-600/80 hover:bg-indigo-600 text-white transition-all shadow-md shadow-indigo-600/20"
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Auto-Gen HR Admin
                </button>
              </>
            )}
          </div>
        </div>

        {/* TAB 1: EXISTING LOGIN FORM */}
        {activeTab === 'login' && (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            {loginError && (
              <div className="p-3.5 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3 text-red-300 text-xs font-medium">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Username</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter username"
                  className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-100 placeholder-slate-500 transition-all outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-100 placeholder-slate-500 transition-all outline-none"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-2 py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50"
            >
              {submitting ? 'Authenticating...' : 'Sign In to IRS Portal'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* TAB 2: NEW USER REGISTRATION FORM */}
        {activeTab === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            {regError && (
              <div className="p-3.5 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3 text-red-300 text-xs font-medium">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>{regError}</span>
              </div>
            )}

            {regSuccess && (
              <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center gap-3 text-emerald-300 text-xs font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{regSuccess}</span>
              </div>
            )}

            {/* Account Role Choice */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Account Role</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRegRole('EMPLOYEE')}
                  className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold transition-all border ${
                    regRole === 'EMPLOYEE'
                      ? 'bg-emerald-950/60 border-emerald-500/60 text-emerald-300 shadow-md shadow-emerald-500/10'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <UserCheck className="w-3.5 h-3.5" />
                  Employee User
                </button>
                <button
                  type="button"
                  onClick={() => setRegRole('HR')}
                  className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold transition-all border ${
                    regRole === 'HR'
                      ? 'bg-indigo-950/60 border-indigo-500/60 text-indigo-300 shadow-md shadow-indigo-500/10'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  HR Administrator
                </button>
              </div>
            </div>

            {/* Username Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">New Username</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="text"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  placeholder="e.g. rohan_dev or hr_vikram"
                  className="w-full bg-slate-950/80 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-100 placeholder-slate-500 transition-all outline-none"
                  required
                />
              </div>
            </div>

            {/* If Employee, select linked employee profile */}
            {regRole === 'EMPLOYEE' && (
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Link Employee Profile
                </label>
                <div className="relative">
                  <Building2 className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                  <select
                    value={regEmployeeId}
                    onChange={(e) => setRegEmployeeId(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-100 transition-all outline-none"
                  >
                    <option value="1">EMP001 - Aarav Sharma (Senior Software Engineer)</option>
                    <option value="2">EMP002 - Priya Nair (Backend Engineer)</option>
                    <option value="3">EMP003 - Ananya Patel (Data Engineer)</option>
                  </select>
                </div>
              </div>
            )}

            {/* Password Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="Create password"
                  className="w-full bg-slate-950/80 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-100 placeholder-slate-500 transition-all outline-none"
                  required
                />
              </div>
            </div>

            {/* Confirm Password Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Confirm Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="password"
                  value={regConfirmPassword}
                  onChange={(e) => setRegConfirmPassword(e.target.value)}
                  placeholder="Confirm password"
                  className="w-full bg-slate-950/80 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-100 placeholder-slate-500 transition-all outline-none"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={regSubmitting}
              className="w-full mt-2 py-3 px-4 bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50"
            >
              {regSubmitting ? 'Creating Account & Registering...' : 'Create Account & Sign In'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default Login;
