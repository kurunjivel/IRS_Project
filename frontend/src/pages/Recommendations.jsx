import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PageContainer from '../components/layout/PageContainer';
import { useCareerAnalysis } from '../hooks/useCareerAnalysis';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

import RecommendationCard from '../components/recommendations/RecommendationCard';
import LearningRecommendations from '../components/recommendations/LearningRecommendations';
import CertificationRecommendations from '../components/recommendations/CertificationRecommendations';
import ProjectRecommendations from '../components/recommendations/ProjectRecommendations';
import MentorRecommendations from '../components/recommendations/MentorRecommendations';
import QuickStats from '../components/dashboard/QuickStats';
import { Lightbulb, BookOpen, Award, Briefcase, Users, Filter } from 'lucide-react';

export const Recommendations = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const empId = Number(employeeId) || 1;

  const [activeTab, setActiveTab] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const { data, loading, error, refetch } = useCareerAnalysis(empId);

  const handleEmployeeChange = (newId) => {
    navigate(`/recommendations/${newId}`);
  };

  if (loading) {
    return (
      <PageContainer title="Personalised Recommendations" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <LoadingSpinner text="Generating hybrid recommendation action plan..." />
      </PageContainer>
    );
  }

  if (error || !data) {
    return (
      <PageContainer title="Personalised Recommendations" employeeId={empId} onEmployeeChange={handleEmployeeChange}>
        <ErrorMessage title="Unable to Load Recommendations" message={error} onRetry={refetch} />
      </PageContainer>
    );
  }

  const { employee, recommendations } = data;
  const learning = recommendations?.learning || [];
  const certs = recommendations?.certifications || [];
  const projects = recommendations?.projects || [];
  const mentors = recommendations?.mentors || [];

  // Filter helper
  const filterByPriority = (items) => {
    if (priorityFilter === 'ALL') return items;
    return items.filter((i) => i.priority?.toUpperCase() === priorityFilter);
  };

  const filteredLearning = filterByPriority(learning);
  const filteredCerts = filterByPriority(certs);
  const filteredProjects = filterByPriority(projects);
  const filteredMentors = filterByPriority(mentors);

  const tabs = [
    { id: 'all', label: 'All Recommendations', icon: Lightbulb, count: learning.length + certs.length + projects.length + mentors.length },
    { id: 'learning', label: 'Learning Paths', icon: BookOpen, count: learning.length },
    { id: 'certifications', label: 'Certifications', icon: Award, count: certs.length },
    { id: 'projects', label: 'Projects', icon: Briefcase, count: projects.length },
    { id: 'mentors', label: 'Mentors', icon: Users, count: mentors.length },
  ];

  return (
    <PageContainer title="Personalised Recommendations" employeeId={empId} employee={employee} onEmployeeChange={handleEmployeeChange}>
      {/* Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Lightbulb className="w-4 h-4" />
            <span>AI-Driven Hybrid Career Growth Plan</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Recommended Action Plan</h1>
          <p className="text-xs text-slate-400 mt-1">
            Prioritised growth interventions synthesizing rule-based gap analysis and machine learning promotion targets.
          </p>
        </div>
      </div>

      {/* TOP SUMMARY STATS */}
      <QuickStats recommendations={recommendations} />

      {/* TABS & PRIORITY FILTER BAR */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-3">
        {/* Category Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all shrink-0 ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${isActive ? 'bg-indigo-500/40 text-white' : 'bg-slate-800 text-slate-400'}`}>
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Priority Filter */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
          <Filter className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-400 font-semibold">Priority:</span>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-transparent text-slate-200 font-bold focus:outline-none cursor-pointer"
          >
            <option value="ALL" className="bg-slate-900">All Priorities</option>
            <option value="HIGH" className="bg-slate-900 text-rose-400">High Priority</option>
            <option value="MEDIUM" className="bg-slate-900 text-amber-400">Medium Priority</option>
            <option value="LOW" className="bg-slate-900 text-slate-300">Low Priority</option>
          </select>
        </div>
      </div>

      {/* CONTENT BASED ON ACTIVE TAB */}
      <div className="space-y-6">
        {(activeTab === 'all' || activeTab === 'learning') && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-400" />
              <span>Learning & Skill Path Recommendations</span>
            </h3>
            <LearningRecommendations items={filteredLearning} />
          </div>
        )}

        {(activeTab === 'all' || activeTab === 'certifications') && (
          <div className="space-y-3 pt-4 border-t border-slate-800/80">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-400" />
              <span>Certification Recommendations</span>
            </h3>
            <CertificationRecommendations items={filteredCerts} />
          </div>
        )}

        {(activeTab === 'all' || activeTab === 'projects') && (
          <div className="space-y-3 pt-4 border-t border-slate-800/80">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-purple-400" />
              <span>Project Assignments</span>
            </h3>
            <ProjectRecommendations items={filteredProjects} />
          </div>
        )}

        {(activeTab === 'all' || activeTab === 'mentors') && (
          <div className="space-y-3 pt-4 border-t border-slate-800/80">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-emerald-400" />
              <span>Mentorship Connect</span>
            </h3>
            <MentorRecommendations items={filteredMentors} />
          </div>
        )}
      </div>
    </PageContainer>
  );
};

export default Recommendations;
