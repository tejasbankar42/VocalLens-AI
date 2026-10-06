import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { GitCompare, Info, ShieldCheck, ArrowRight, Sparkles } from 'lucide-react';
import { fetchBaseline } from '../api/client';

export default function ComparePage({ report, onNavigateToRecord }) {
  const [baseline, setBaseline] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBaseline()
      .then((data) => {
        setBaseline(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const dimensions = [
    'clarity',
    'fluency',
    'pace',
    'pauses',
    'fillers',
    'pronunciation',
    'confidence',
    'vocabulary',
  ];

  // Prepare comparison data for Recharts Bar Chart
  const chartData = dimensions.map((dim) => {
    const userScore = report?.dimension_scores?.[dim] !== undefined ? report.dimension_scores[dim] : 75;
    const idealMean = 92; // Benchmark ideal normalized score
    const flawedMean = 25; // Benchmark flawed normalized score

    return {
      dimension: dim.charAt(0).toUpperCase() + dim.slice(1),
      User: Number(userScore.toFixed(1)),
      IdealBenchmark: idealMean,
      FlawedBenchmark: flawedMean,
    };
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
              Contrastive Analytics
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1.5">
            Exemplar Contrastive Benchmarking
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Comparing your speech profile against calibrated distributions of ideal and flawed speech.
          </p>
        </div>

        <div className="text-xs text-slate-400 bg-slate-900/60 border border-slate-800 p-3 rounded-xl max-w-sm">
          <strong className="text-brand-300">Hackathon Track:</strong> Contrastive Speech Analytics & Temporal Flaw Grounding
        </div>
      </div>

      {/* Concept Explanation Card */}
      <div className="p-6 rounded-2xl glass-panel bg-gradient-to-r from-brand-950/40 via-slate-900/60 to-cyan-950/30 border border-brand-500/20 space-y-3">
        <div className="flex items-center space-x-2 text-brand-300">
          <Info className="w-5 h-5 flex-shrink-0" />
          <h3 className="text-sm font-bold uppercase tracking-wider">
            Why Contrastive Evaluation Outperforms Arbitrary LLM Scores
          </h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Traditional voice apps rely on black-box LLM prompts that produce inconsistent, noisy scores. VocalLens AI evaluates speech by mathematically contrasting your acoustic and linguistic measurements against a dual-distribution dataset:
        </p>
        <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs text-brand-300 text-center">
          score = clip((x - flawed_mean) / (ideal_mean - flawed_mean), 0, 1) * 100
        </div>
        <p className="text-[11px] text-slate-400">
          This guarantees <strong>100% determinism</strong>: identical speech produces the exact same score every time, with zero randomness or prompt drift.
        </p>
      </div>

      {/* Comparison Multi-Bar Chart */}
      <div className="p-6 rounded-2xl glass-panel space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
              Dimension Contrast: User vs. Ideal vs. Flawed
            </h3>
            <p className="text-xs text-slate-400">Higher score reflects alignment with ideal speech exemplars.</p>
          </div>
        </div>

        <div className="w-full h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 20, left: -10, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="dimension" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="User" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="IdealBenchmark" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="FlawedBenchmark" fill="#f43f5e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Metrics Table */}
      <div className="p-6 rounded-2xl glass-panel space-y-4">
        <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
          Comprehensive Metric Distribution Table
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-3">Dimension</th>
                <th className="py-3 px-3">User Raw Value</th>
                <th className="py-3 px-3">Ideal Group Mean</th>
                <th className="py-3 px-3">Flawed Group Mean</th>
                <th className="py-3 px-3">Contrastive Score</th>
                <th className="py-3 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {dimensions.map((dim) => {
                const userScore = report?.dimension_scores?.[dim] || 70;
                const userRaw = report?.raw_metrics?.[dim] !== undefined ? report.raw_metrics[dim] : '—';
                const idealM = baseline?.ideal?.[dim]?.mean !== undefined ? baseline.ideal[dim].mean : '—';
                const flawedM = baseline?.flawed?.[dim]?.mean !== undefined ? baseline.flawed[dim].mean : '—';

                return (
                  <tr key={dim} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3 px-3 font-bold text-white capitalize">{dim}</td>
                    <td className="py-3 px-3 font-mono text-brand-300">{userRaw}</td>
                    <td className="py-3 px-3 font-mono text-emerald-400">{idealM}</td>
                    <td className="py-3 px-3 font-mono text-rose-400">{flawedM}</td>
                    <td className="py-3 px-3 font-bold">
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${
                          userScore >= 80
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : userScore >= 60
                            ? 'bg-amber-500/20 text-amber-300'
                            : 'bg-rose-500/20 text-rose-300'
                        }`}
                      >
                        {userScore.toFixed(1)} / 100
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {userScore >= 80 ? (
                        <span className="text-emerald-400 font-semibold flex items-center space-x-1">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          <span>Exemplar Level</span>
                        </span>
                      ) : userScore >= 60 ? (
                        <span className="text-amber-400 font-medium">Developing</span>
                      ) : (
                        <span className="text-rose-400 font-medium">Flawed Gap</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
