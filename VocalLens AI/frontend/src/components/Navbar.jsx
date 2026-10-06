import React, { useState } from 'react';
import { Mic, BarChart2, GitCompare, TrendingUp, Database, Sparkles, Sun, Moon, Volume2 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onSelectDemo, isDark, setIsDark }) {
  const [demoOpen, setDemoOpen] = useState(false);

  const navItems = [
    { id: 'record', label: 'Record & Analyze', icon: Mic },
    { id: 'report', label: 'Speech Report', icon: BarChart2 },
    { id: 'compare', label: 'Contrastive Compare', icon: GitCompare },
    { id: 'progress', label: 'Progress Analytics', icon: TrendingUp },
    { id: 'dataset', label: 'Dataset & Rubric', icon: Database },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Name */}
          <div 
            className="flex items-center space-x-3 cursor-pointer group"
            onClick={() => setActiveTab('record')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform duration-200">
              <Mic className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-white group-hover:text-brand-300 transition-colors">
                  VocalLens <span className="text-brand-400 font-extrabold">AI</span>
                </span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20">
                  Contrastive
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block tracking-wide">
                Speak. Measure. Improve.
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-brand-500/15 text-brand-300 border border-brand-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Action Area: Demo Mode + Theme Toggle */}
          <div className="flex items-center space-x-2.5">
            {/* Demo Mode Dropdown */}
            <div className="relative">
              <button
                onClick={() => setDemoOpen(!demoOpen)}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-amber-500/20 to-orange-500/20 hover:from-amber-500/30 hover:to-orange-500/30 text-amber-300 border border-amber-500/30 shadow-sm transition-all"
                title="Load pre-analyzed demo sessions for judges"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Demo Mode</span>
              </button>

              {demoOpen && (
                <div 
                  className="absolute right-0 mt-2 w-64 rounded-xl border border-slate-800 bg-slate-900/95 backdrop-blur-xl shadow-2xl p-2 z-50 text-xs animate-in fade-in zoom-in-95 duration-100"
                  onMouseLeave={() => setDemoOpen(false)}
                >
                  <p className="px-2 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Instant Judge Showcase
                  </p>
                  <button
                    onClick={() => {
                      onSelectDemo('flagship');
                      setDemoOpen(false);
                    }}
                    className="w-full text-left p-2 rounded-lg hover:bg-slate-800/80 text-slate-200 transition-colors flex flex-col"
                  >
                    <span className="font-semibold text-emerald-400 flex items-center justify-between">
                      Flagship Presentation <span>89.5 pts</span>
                    </span>
                    <span className="text-[11px] text-slate-400 mt-0.5">
                      Ideal cadence, high vocabulary, zero fillers
                    </span>
                  </button>
                  <button
                    onClick={() => {
                      onSelectDemo('flawed');
                      setDemoOpen(false);
                    }}
                    className="w-full text-left p-2 rounded-lg hover:bg-slate-800/80 text-slate-200 transition-colors flex flex-col mt-1 border-t border-slate-800/60 pt-2"
                  >
                    <span className="font-semibold text-rose-400 flex items-center justify-between">
                      Disfluent Speech Sample <span>51.8 pts</span>
                    </span>
                    <span className="text-[11px] text-slate-400 mt-0.5">
                      Temporal flaw markers: long pauses, repetitions, fillers
                    </span>
                  </button>
                </div>
              )}
            </div>

            {/* Dark / Light Mode Toggle */}
            <button
              onClick={() => setIsDark(!isDark)}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-slate-800/80 transition-colors"
              title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-300" /> : <Moon className="w-4 h-4 text-slate-400" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
