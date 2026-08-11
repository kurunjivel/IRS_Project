import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const PageContainer = ({
  title,
  employeeId = 1,
  employee,
  onEmployeeChange,
  children,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      {/* Sidebar */}
      <Sidebar
        employeeId={employeeId}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        {/* Top Header */}
        <Header
          title={title}
          employee={employee}
          selectedEmpId={employeeId}
          onEmployeeChange={onEmployeeChange}
          onToggleSidebar={() => setSidebarOpen(true)}
        />

        {/* Page Content Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default PageContainer;
