import React from 'react';

export default function MetricCard({ title, value, unit = '', subtext, icon: Icon, trend }) {
  return (
    <div className="p-4 rounded-xl glass-panel relative overflow-hidden flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className="w-7 h-7 rounded-lg bg-slate-800/80 flex items-center justify-center text-brand-400">
            <Icon className="w-3.5 h-3.5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline space-x-1.5 my-1">
        <span className="text-2xl font-bold tracking-tight text-white">{value}</span>
        {unit && <span className="text-xs text-slate-400 font-medium">{unit}</span>}
      </div>

      {subtext && (
        <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">
          {subtext}
        </p>
      )}
    </div>
  );
}
