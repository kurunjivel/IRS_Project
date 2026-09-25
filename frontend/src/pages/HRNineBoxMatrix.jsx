import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getNineBoxMatrix } from '../api/hrApi';
import {
  Grid,
  Filter,
  CheckCircle,
  Clock,
  AlertTriangle,
  Users,
  ChevronRight,
  TrendingUp,
  Award,
  Zap,
} from 'lucide-react';

export const HRNineBoxMatrix = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);

  // Filters state
  const [department, setDepartment] = useState('');
  const [currentGrade, setCurrentGrade] = useState('');
  const [targetGrade, setTargetGrade] = useState('');

  useEffect(() => {
    fetchMatrix();
  }, [department, currentGrade, targetGrade]);

  const fetchMatrix = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (department) params.department = department;
      if (currentGrade) params.current_grade = currentGrade;
      if (targetGrade) params.target_grade = targetGrade;

      const res = await getNineBoxMatrix(params);
      setData(res.grid ? res : (res.data || res));
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to load 9-Box Succession Matrix.');
    } finally {
      setLoading(false);
    }
  };

  const getCellColor = (boxId) => {
    switch (boxId) {
      case 'HIGH_HIGH':
        return 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400';
      case 'HIGH_MEDIUM':
        return 'border-teal-500/40 bg-teal-500/10 text-teal-400';
      case 'HIGH_LOW':
        return 'border-amber-500/40 bg-amber-500/10 text-amber-400';
      case 'MEDIUM_HIGH':
        return 'border-blue-500/40 bg-blue-500/10 text-blue-400';
      case 'MEDIUM_MEDIUM':
        return 'border-slate-600 bg-slate-800/80 text-slate-300';
      case 'MEDIUM_LOW':
        return 'border-orange-500/40 bg-orange-500/10 text-orange-400';
      case 'LOW_HIGH':
        return 'border-indigo-500/40 bg-indigo-500/10 text-indigo-400';
      case 'LOW_MEDIUM':
        return 'border-purple-500/40 bg-purple-500/10 text-purple-400';
      case 'LOW_LOW':
        return 'border-rose-500/40 bg-rose-500/10 text-rose-400';
      default:
        return 'border-slate-700 bg-slate-800/50 text-slate-300';
    }
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-400"></div>
      </div>
    );
  }

  const pipeline = data?.pipeline_summary || {
    READY_NOW: 0,
    READY_SOON: 0,
    DEVELOPMENT_REQUIRED: 0,
    TALENT_BOTTLENECK: 0,
  };

  const grid = data?.grid || {};

  // 3x3 layout ordering: Y (Readiness) rows: HIGH, MEDIUM, LOW; X (Performance) cols: LOW, MEDIUM, HIGH
  const rows = ['HIGH', 'MEDIUM', 'LOW'];
  const cols = ['LOW', 'MEDIUM', 'HIGH'];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-800/80 p-6 rounded-2xl border border-slate-700/60 shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Grid className="w-7 h-7 text-emerald-400" />
            HR 9-Box Succession Planning Matrix
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Map workforce talent across Performance (X-Axis) vs IRS Readiness Score (Y-Axis) for succession planning.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Succession Pipeline Indicator Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Ready Now</span>
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2">{pipeline.READY_NOW}</div>
          <p className="text-slate-500 text-xs mt-1">Immediate promotion candidates</p>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Ready Soon</span>
            <Clock className="w-5 h-5 text-teal-400" />
          </div>
          <div className="text-3xl font-extrabold text-teal-400 mt-2">{pipeline.READY_SOON}</div>
          <p className="text-slate-500 text-xs mt-1">Targeted 6-12 mo timeline</p>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Development Required</span>
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400 mt-2">{pipeline.DEVELOPMENT_REQUIRED}</div>
          <p className="text-slate-500 text-xs mt-1">Gap closing focus needed</p>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 p-5 rounded-xl shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Talent Bottlenecks</span>
            <Zap className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-indigo-400 mt-2">{pipeline.TALENT_BOTTLENECK}</div>
          <p className="text-slate-500 text-xs mt-1">High readiness / low perf focus</p>
        </div>
      </div>

      {/* Filter Control Bar */}
      <div className="bg-slate-800/80 border border-slate-700/60 p-4 rounded-xl shadow-md flex flex-wrap gap-4 items-center">
        <div className="flex items-center space-x-2 text-slate-300 text-sm font-semibold">
          <Filter className="w-4 h-4 text-emerald-400" />
          <span>Filters:</span>
        </div>

        <div className="w-48">
          <input
            type="text"
            placeholder="Department (e.g. Engineering)"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="w-40">
          <input
            type="text"
            placeholder="Current Grade (e.g. G2)"
            value={currentGrade}
            onChange={(e) => setCurrentGrade(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="w-40">
          <input
            type="text"
            placeholder="Target Grade (e.g. G3)"
            value={targetGrade}
            onChange={(e) => setTargetGrade(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>

        {(department || currentGrade || targetGrade) && (
          <button
            onClick={() => {
              setDepartment('');
              setCurrentGrade('');
              setTargetGrade('');
            }}
            className="text-xs text-rose-400 hover:underline"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* 9-Box Visual Grid (3x3 Matrix) */}
      <div className="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl space-y-4">
        <div className="flex justify-between items-center border-b border-slate-700/60 pb-3">
          <div className="text-sm font-bold text-slate-200">
            Performance (X-Axis) vs Readiness Score (Y-Axis)
          </div>
          <div className="text-xs text-slate-400">
            Total Analyzed: <strong className="text-emerald-400">{data?.total_analyzed || 0}</strong> employees
          </div>
        </div>

        {/* Column Headers (X-Axis: Performance) */}
        <div className="grid grid-cols-4 gap-3 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <div></div>
          <div className="py-1 bg-slate-900/50 rounded">Low Perf (&lt; 3.0)</div>
          <div className="py-1 bg-slate-900/50 rounded">Med Perf (3.0–3.9)</div>
          <div className="py-1 bg-slate-900/50 rounded">High Perf (&ge; 4.0)</div>
        </div>

        {/* Matrix Grid Rows */}
        {rows.map((rLevel) => (
          <div key={rLevel} className="grid grid-cols-4 gap-3">
            {/* Y-Axis Label */}
            <div className="flex items-center justify-center p-2 bg-slate-900/50 rounded text-xs font-semibold text-slate-400 uppercase tracking-wider text-center">
              {rLevel === 'HIGH' && 'High Readiness (≥ 80)'}
              {rLevel === 'MEDIUM' && 'Med Readiness (60–79)'}
              {rLevel === 'LOW' && 'Low Readiness (< 60)'}
            </div>

            {/* 3 Columns */}
            {cols.map((pLevel) => {
              const boxId = `${pLevel}_${rLevel}`;
              const cell = grid[boxId] || {
                title: boxId,
                count: 0,
                percentage: 0,
                employees: [],
              };
              const isSelected = selectedCell === boxId;

              return (
                <div
                  key={boxId}
                  onClick={() => setSelectedCell(isSelected ? null : boxId)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between min-h-[140px] ${getCellColor(
                    boxId
                  )} ${isSelected ? 'ring-2 ring-emerald-400 scale-[1.02]' : 'hover:border-slate-500'}`}
                >
                  <div>
                    <div className="flex justify-between items-start">
                      <h3 className="font-bold text-xs leading-tight">{cell.title}</h3>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-slate-900/60">
                        {cell.count} ({cell.percentage}%)
                      </span>
                    </div>
                    <p className="text-[11px] opacity-80 mt-1 line-clamp-2">{cell.description}</p>
                  </div>

                  {cell.employees?.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-slate-700/40 text-[11px] flex justify-between items-center">
                      <span className="font-semibold">{cell.employees.length} candidate(s)</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Selected Cell Employee Roster Drawer */}
      {selectedCell && grid[selectedCell] && (
        <div className="bg-slate-800/90 border border-emerald-500/40 p-6 rounded-2xl shadow-2xl space-y-4">
          <div className="flex justify-between items-center border-b border-slate-700/60 pb-3">
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Users className="w-5 h-5 text-emerald-400" />
                {grid[selectedCell].title} Roster
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">{grid[selectedCell].description}</p>
            </div>
            <button
              onClick={() => setSelectedCell(null)}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Close
            </button>
          </div>

          {grid[selectedCell].employees?.length === 0 ? (
            <p className="text-xs text-slate-500">No employees classified in this cell.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {grid[selectedCell].employees.map((emp) => (
                <div
                  key={emp.employee_id}
                  onClick={() => navigate(`/hr/employees/${emp.employee_id}`)}
                  className="bg-slate-900/80 border border-slate-700/60 p-4 rounded-xl hover:border-emerald-500 transition-all cursor-pointer space-y-2 group"
                >
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-sm text-slate-100 group-hover:text-emerald-400 transition-colors">
                      {emp.full_name}
                    </h3>
                    <span className="text-[10px] px-2 py-0.5 bg-slate-800 text-slate-300 rounded font-semibold">
                      {emp.current_grade} → {emp.target_grade}
                    </span>
                  </div>

                  <div className="text-xs text-slate-400">{emp.department}</div>

                  <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-800">
                    <div>
                      <span className="text-[10px] text-slate-500 block">Performance</span>
                      <strong className="text-slate-200">{emp.performance_rating} / 5.0</strong>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 block">Readiness Score</span>
                      <strong className="text-emerald-400">{emp.readiness_score?.toFixed(1)} / 100</strong>
                    </div>
                  </div>

                  <div className="flex justify-end pt-1">
                    <span className="text-[11px] text-emerald-400 group-hover:underline flex items-center gap-1 font-medium">
                      View Full Analysis <ChevronRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
