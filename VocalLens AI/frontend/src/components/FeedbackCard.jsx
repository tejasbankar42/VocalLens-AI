import React from 'react';
import { Target, Lightbulb, Zap, ArrowUpRight } from 'lucide-react';

export default function FeedbackCard({ tip }) {
  const priorityConfig = {
    high: {
      badge: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
      icon: Zap,
      border: 'hover:border-rose-500/40',
    },
    medium: {
      badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
      icon: Target,
      border: 'hover:border-amber-500/40',
    },
    low: {
      badge: 'bg-teal-500/15 text-teal-300 border-teal-500/30',
      icon: Lightbulb,
      border: 'hover:border-teal-500/40',
    },
  };

  const current = priorityConfig[tip.priority] || priorityConfig.medium;
  const Icon = current.icon;

  return (
    <div className={`p-5 rounded-xl bg-slate-900/80 border border-slate-800/80 ${current.border} transition-all duration-200 flex flex-col justify-between group shadow-sm`}>
      <div>
        <div className="flex items-center justify-between gap-2 mb-2.5">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center text-brand-400 group-hover:scale-105 transition-transform">
              <Icon className="w-3.5 h-3.5" />
            </div>
            <h4 className="text-sm font-bold text-slate-100 group-hover:text-brand-300 transition-colors">
              {tip.title}
            </h4>
          </div>
          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border ${current.badge}`}>
            {tip.priority} Priority
          </span>
        </div>

        {/* Observation / What to improve */}
        <div className="mb-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            What was observed:
          </span>
          <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/40">
            {tip.observation}
          </p>
        </div>

        {/* How to improve */}
        <div>
          <span className="text-[10px] font-semibold text-brand-400 uppercase tracking-wider block mb-1">
            How to improve:
          </span>
          <p className="text-xs text-slate-200 leading-relaxed font-medium">
            {tip.how_to_improve}
          </p>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
        <span className="capitalize font-mono">Dimension: {tip.dimension}</span>
        <span className="text-brand-400 font-medium flex items-center group-hover:translate-x-0.5 transition-transform">
          Pedagogical Drill <ArrowUpRight className="w-3 h-3 ml-0.5" />
        </span>
      </div>
    </div>
  );
}
