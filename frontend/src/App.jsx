import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';

// Auth Page
import Login from './pages/Login';

// Layouts
import EmployeeLayout from './components/layout/EmployeeLayout';
import HRLayout from './components/layout/HRLayout';
import { ManagerLayout } from './components/layout/ManagerLayout';

// Employee Portal Pages
import EmployeeDashboard from './pages/EmployeeDashboard';
import EmployeeProfileView from './pages/EmployeeProfileView';
import EmployeeSkillGapsView from './pages/EmployeeSkillGapsView';
import EmployeeRecommendationsView from './pages/EmployeeRecommendationsView';
import EmployeeRoadmapView from './pages/EmployeeRoadmapView';
import EmployeeProgressView from './pages/EmployeeProgressView';
import EmployeePromotionStatusView from './pages/EmployeePromotionStatusView';
import EmployeeWhatIfSimulator from './pages/EmployeeWhatIfSimulator';
import MentorMatchingView from './pages/MentorMatchingView';
import EmployeeCareerStabilityView from './pages/EmployeeCareerStabilityView';
import ResumeParserView from './pages/ResumeParserView';

// HR Dashboard Pages
import HRDashboard from './pages/HRDashboard';
import HRRoleFitView from './pages/HRRoleFitView';
import HREmployeesView from './pages/HREmployeesView';
import HREmployeeDetailView from './pages/HREmployeeDetailView';
import HRAnalyticsView from './pages/HRAnalyticsView';
import { HRNineBoxMatrix } from './pages/HRNineBoxMatrix';

// Manager Portal Pages
import { ManagerDashboard } from './pages/ManagerDashboard';
import { ManagerEmployeeDetailView } from './pages/ManagerEmployeeDetailView';

const HomeRedirect = () => {
  const { user, isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (user?.role === 'HR') return <Navigate to="/hr" replace />;
  if (user?.role === 'MANAGER') return <Navigate to="/manager" replace />;
  return <Navigate to="/employee" replace />;
};

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Root Redirect */}
          <Route path="/" element={<HomeRedirect />} />

          {/* Authentication */}
          <Route path="/login" element={<Login />} />

          {/* Employee Self-Service Portal Routes */}
          <Route
            path="/employee"
            element={
              <ProtectedRoute allowedRole="EMPLOYEE">
                <EmployeeLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<EmployeeDashboard />} />
            <Route path="profile" element={<EmployeeProfileView />} />
            <Route path="career-analysis" element={<EmployeeDashboard />} />
            <Route path="skills" element={<EmployeeSkillGapsView />} />
            <Route path="recommendations" element={<EmployeeRecommendationsView />} />
            <Route path="mentors" element={<MentorMatchingView />} />
            <Route path="stability" element={<EmployeeCareerStabilityView />} />
            <Route path="resume" element={<ResumeParserView />} />
            <Route path="roadmap" element={<EmployeeRoadmapView />} />
            <Route path="progress" element={<EmployeeProgressView />} />
            <Route path="promotion" element={<EmployeePromotionStatusView />} />
            <Route path="simulator" element={<EmployeeWhatIfSimulator />} />
          </Route>

          {/* Manager Portal Routes */}
          <Route
            path="/manager"
            element={
              <ProtectedRoute allowedRole="MANAGER">
                <ManagerLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<ManagerDashboard />} />
            <Route path="reviews" element={<ManagerDashboard />} />
            <Route path="candidates" element={<ManagerDashboard />} />
            <Route path="employee/:employeeId" element={<ManagerEmployeeDetailView />} />
          </Route>

          {/* HR Administration Portal Routes */}
          <Route
            path="/hr"
            element={
              <ProtectedRoute allowedRole="HR">
                <HRLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<HRDashboard />} />
            <Route path="roles" element={<HRRoleFitView />} />
            <Route path="succession" element={<HRNineBoxMatrix />} />
            <Route path="employees" element={<HREmployeesView />} />
            <Route path="employees/:employeeId" element={<HREmployeeDetailView />} />
            <Route path="requirements" element={<HRRoleFitView />} />
            <Route path="analytics" element={<HRAnalyticsView />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<HomeRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
