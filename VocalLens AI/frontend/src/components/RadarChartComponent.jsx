import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

export default function RadarChartComponent({ dimensionScores = {} }) {
  const dimensionLabels = {
    clarity: 'Clarity',
    fluency: 'Fluency',
    pace: 'Pace',
    pauses: 'Pauses',
    fillers: 'Fillers',
    pronunciation: 'Pronunciation',
    confidence: 'Confidence',
    vocabulary: 'Vocabulary',
  };

  const data = Object.keys(dimensionLabels).map((key) => ({
    dimension: dimensionLabels[key],
    score: dimensionScores[key] !== undefined ? dimensionScores[key] : 70,
    fullMark: 100,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700/80 px-3 py-2 rounded-lg shadow-xl text-xs text-slate-100">
          <p className="font-bold text-brand-400">{item.dimension}</p>
          <p className="text-slate-300">
            Score: <span className="font-semibold text-white">{item.score}</span> / 100
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-6 rounded-2xl glass-panel flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-400">
          8-Dimension Speech Radar
        </h3>
        <span className="text-[11px] text-slate-400 font-medium">Weighted Rubric</span>
      </div>

      <div className="w-full h-64 sm:h-72">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
            <PolarGrid stroke="#334155" strokeDasharray="3 3" />
            <PolarAngleAxis
              dataKey="dimension"
              tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 500 }}
            />
            <PolarRadiusAxis
              angle={30}
              domain={[0, 100]}
              tick={{ fill: '#64748b', fontSize: 10 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Radar
              name="User"
              dataKey="score"
              stroke="#14b8a6"
              fill="#14b8a6"
              fillOpacity={0.45}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-800/80 text-center">
        {data.slice(0, 4).map((d) => (
          <div key={d.dimension} className="text-center">
            <span className="text-[10px] text-slate-400 truncate block">{d.dimension}</span>
            <span className="text-xs font-bold text-slate-200">{d.score}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
