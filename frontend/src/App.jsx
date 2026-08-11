import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Pages
import Dashboard from './pages/Dashboard';
import EmployeeProfile from './pages/EmployeeProfile';
import GapAnalysis from './pages/GapAnalysis';
import Readiness from './pages/Readiness';
import Recommendations from './pages/Recommendations';
import CareerAnalysis from './pages/CareerAnalysis';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/employee/:employeeId" element={<EmployeeProfile />} />
        <Route path="/gap-analysis/:employeeId" element={<GapAnalysis />} />
        <Route path="/readiness/:employeeId" element={<Readiness />} />
        <Route path="/recommendations/:employeeId" element={<Recommendations />} />
        <Route path="/career-analysis/:employeeId" element={<CareerAnalysis />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
