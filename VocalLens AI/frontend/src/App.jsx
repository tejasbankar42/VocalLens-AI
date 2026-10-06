import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import RecordPage from './pages/RecordPage';
import ReportPage from './pages/ReportPage';
import ComparePage from './pages/ComparePage';
import ProgressPage from './pages/ProgressPage';
import DatasetInsightsPage from './pages/DatasetInsightsPage';
import { fetchDemoSession, fetchSessionDetail } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('record');
  const [currentReport, setCurrentReport] = useState(null);
  const [isDark, setIsDark] = useState(true);

  // Sync dark class with document element
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // Load demo flagship session into state on mount so all tabs are populated immediately
  useEffect(() => {
    fetchDemoSession('flagship')
      .then((data) => {
        setCurrentReport(data);
      })
      .catch((err) => {
        console.warn('Initial demo fetch:', err);
      });
  }, []);

  const handleAnalysisComplete = (newReport) => {
    setCurrentReport(newReport);
    setActiveTab('report');
  };

  const handleSelectDemo = async (type) => {
    try {
      const demoData = await fetchDemoSession(type);
      setCurrentReport(demoData);
      setActiveTab('report');
    } catch (err) {
      console.error('Failed to load demo session:', err);
    }
  };

  const handleSelectSession = async (sessionId) => {
    try {
      const sessionData = await fetchSessionDetail(sessionId);
      setCurrentReport(sessionData);
      setActiveTab('report');
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-200 ${
      isDark ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'
    }`}>
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onSelectDemo={handleSelectDemo}
        isDark={isDark}
        setIsDark={setIsDark}
      />

      {/* Main View Area */}
      <main className="flex-1">
        {activeTab === 'record' && (
          <RecordPage
            onAnalysisComplete={handleAnalysisComplete}
            onSelectDemo={handleSelectDemo}
          />
        )}
        {activeTab === 'report' && (
          <ReportPage
            report={currentReport}
            onNavigateToCompare={() => setActiveTab('compare')}
            onNavigateToRecord={() => setActiveTab('record')}
          />
        )}
        {activeTab === 'compare' && (
          <ComparePage
            report={currentReport}
            onNavigateToRecord={() => setActiveTab('record')}
          />
        )}
        {activeTab === 'progress' && (
          <ProgressPage onSelectSession={handleSelectSession} />
        )}
        {activeTab === 'dataset' && <DatasetInsightsPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-300">VocalLens AI</span>
            <span>—</span>
            <span className="italic">Speak. Measure. Improve.</span>
          </div>
          <div>
            Contrastive Speech Analytics & Temporal Flaw Grounding
          </div>
        </div>
      </footer>
    </div>
  );
}
