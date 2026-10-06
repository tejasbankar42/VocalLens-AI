import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, Award, Calendar, ChevronRight, Sparkles, CheckCircle2 } from 'lucide-react';
import { fetchProgress, fetchSessionDetail } from '../api/client';

export default function ProgressPage({ onSelectSession }) {
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress()
      .then((data) => {
        setProgressData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center text-slate-400 text-sm">
        Loading historical progress analytics...
      </div>
    );
  }

  const {
    total_sessions = 0,
    average_score = 0,
    highest_score = 0,
    most_improved_dimension = 'Clarity',
    improvement_delta = 0,
    score_history = [],
    recent_sessions = [],
  } = progressData || {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="pb-6 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
            Longitudinal Tracking
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1.5">
          Speech Improvement Trajectory
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Review your communication score trajectory across multiple practice recordings.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-panel flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Practice Sessions</span>
          <div className="my-2">
            <span className="text-3xl font-black text-white">{total_sessions}</span>
          </div>
          <p className="text-[11px] text-slate-400">Consistent practice build</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Average Score</span>
          <div className="my-2">
            <span className="text-3xl font-black text-brand-300">{average_score}</span>
            <span className="text-xs text-slate-400 ml-1">/ 100</span>
          </div>
          <p className="text-[11px] text-slate-400">Across all sessions</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Personal Best</span>
          <div className="my-2">
            <span className="text-3xl font-black text-emerald-400">{highest_score}</span>
            <span className="text-xs text-slate-400 ml-1">/ 100</span>
          </div>
          <p className="text-[11px] text-emerald-400 font-medium">Flagship session standard</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel bg-gradient-to-br from-brand-950/60 to-emerald-950/40 border border-brand-500/30 flex flex-col justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-brand-300 flex items-center space-x-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Most Improved</span>
          </span>
          <div className="my-2">
            <span className="text-2xl font-black text-white capitalize">{most_improved_dimension}</span>
            <span className="text-xs font-bold text-emerald-300 ml-2">+{improvement_delta} pts</span>
          </div>
          <p className="text-[11px] text-slate-300">Fastest growing dimension</p>
        </div>
      </div>

      {/* Progress Line Chart */}
      <div className="p-6 rounded-2xl glass-panel space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
              Communication Score Growth Over Time
            </h3>
            <p className="text-xs text-slate-400">Progressive improvement from baseline disfluency to exemplar poise.</p>
          </div>
        </div>

        <div className="w-full h-72">
          {score_history.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={score_history} margin={{ top: 20, right: 20, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis domain={[40, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#14b8a6"
                  strokeWidth={3}
                  dot={{ r: 5, fill: '#14b8a6', strokeWidth: 2, stroke: '#0f172a' }}
                  activeDot={{ r: 7, fill: '#2dd4bf' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-500">
              No historical data available. Record your first session to initiate tracking.
            </div>
          )}
        </div>
      </div>

      {/* Session History Table */}
      <div className="p-6 rounded-2xl glass-panel space-y-4">
        <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
          Practice Session History
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-3">Session & Recording</th>
                <th className="py-3 px-3">Score</th>
                <th className="py-3 px-3">Band</th>
                <th className="py-3 px-3">Cadence (WPM)</th>
                <th className="py-3 px-3">Fillers</th>
                <th className="py-3 px-3">Pauses</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {recent_sessions.map((s) => (
                <tr key={s.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-3">
                    <span className="font-bold text-white block">{s.filename}</span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(s.created_at).toLocaleDateString()}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-bold font-mono text-brand-300">
                    {s.overall_score} / 100
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold uppercase ${
                        s.band === 'Excellent'
                          ? 'bg-emerald-500/15 text-emerald-300'
                          : s.band === 'Good'
                          ? 'bg-teal-500/15 text-teal-300'
                          : s.band === 'Needs work'
                          ? 'bg-amber-500/15 text-amber-300'
                          : 'bg-rose-500/15 text-rose-300'
                      }`}
                    >
                      {s.band}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono">{s.wpm}</td>
                  <td className="py-3 px-3 font-mono">{s.filler_count}</td>
                  <td className="py-3 px-3 font-mono">{s.pause_count}</td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => onSelectSession(s.id)}
                      className="inline-flex items-center space-x-1 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-brand-300 font-medium text-xs transition-colors"
                    >
                      <span>View</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
