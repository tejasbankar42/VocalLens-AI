import React from 'react';

export default function ScoreGauge({ score = 0, band = 'Needs work' }) {
  const clampedScore = Math.max(0, Math.min(100, Number(score) || 0));
  
  // Radial circular calculations
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  // Band styles
  const bandConfig = {
    Excellent: {
      color: 'text-emerald-400',
      stroke: '#34d399',
      bgGlow: 'from-emerald-500/10 to-teal-500/5',
      badgeBg: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300',
      description: 'Exceptional communication clarity, pace & poise.',
    },
    Good: {
      color: 'text-teal-400',
      stroke: '#2dd4bf',
      bgGlow: 'from-teal-500/10 to-cyan-500/5',
      badgeBg: 'bg-teal-500/15 border-teal-500/30 text-teal-300',
      description: 'Solid delivery with minor polish opportunities.',
    },
    'Needs work': {
      color: 'text-amber-400',
      stroke: '#fbbf24',
      bgGlow: 'from-amber-500/10 to-orange-500/5',
      badgeBg: 'bg-amber-500/15 border-amber-500/30 text-amber-300',
      description: 'Noticeable pacing hesitations or filler patterns.',
    },
    Weak: {
      color: 'text-rose-400',
      stroke: '#f87171',
      bgGlow: 'from-rose-500/10 to-red-500/5',
      badgeBg: 'bg-rose-500/15 border-rose-500/30 text-rose-300',
      description: 'High disfluency, frequent pauses, or low confidence.',
    },
  };

  const current = bandConfig[band] || bandConfig['Needs work'];

  return (
    <div className={`p-6 rounded-2xl glass-panel relative overflow-hidden flex flex-col items-center text-center bg-gradient-to-b ${current.bgGlow}`}>
      <span className="text-xs font-semibold tracking-wider uppercase text-slate-400 mb-3">
        Overall Communication Score
      </span>

      {/* SVG Radial Gauge */}
      <div className="relative w-44 h-44 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 160 160">
          {/* Background circle */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke="currentColor"
            strokeWidth="11"
            className="text-slate-800/80"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke={current.stroke}
            strokeWidth="11"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            fill="transparent"
          />
        </svg>

        {/* Center Score Typography */}
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-4xl font-black tracking-tight text-white">
            {clampedScore.toFixed(1)}
          </span>
          <span className="text-xs text-slate-400 font-medium -mt-0.5">out of 100</span>
        </div>
      </div>

      {/* Band Badge */}
      <div className="mt-4 flex flex-col items-center">
        <span className={`px-3.5 py-1 rounded-full text-xs font-bold border tracking-wide uppercase ${current.badgeBg}`}>
          {band}
        </span>
        <p className="text-xs text-slate-400 mt-2 max-w-xs leading-relaxed">
          {current.description}
        </p>
      </div>
    </div>
  );
}
