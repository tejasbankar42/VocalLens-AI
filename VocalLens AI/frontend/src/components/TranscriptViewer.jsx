import React, { useState } from 'react';
import { FileText, Clock, AlertCircle } from 'lucide-react';

export default function TranscriptViewer({
  words = [],
  flawEvents = [],
  onWordClick = () => {},
  selectedTime = null,
}) {
  const [filterType, setFilterType] = useState('all');

  // Match words with flaw events
  const findFlawForWord = (word) => {
    return flawEvents.find(
      (flaw) =>
        (word.start >= flaw.start - 0.1 && word.start <= flaw.end + 0.1) ||
        (word.end >= flaw.start - 0.1 && word.end <= flaw.end + 0.1)
    );
  };

  return (
    <div className="p-6 rounded-2xl glass-panel flex flex-col h-full">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-brand-400" />
          <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
            Interactive Word-Level Transcript
          </h3>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1.5 text-[11px]">
          {['all', 'flaws', 'low-confidence'].map((f) => (
            <button
              key={f}
              onClick={() => setFilterType(f)}
              className={`px-2.5 py-1 rounded-md capitalize font-medium transition-colors ${
                filterType === f
                  ? 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
                  : 'text-slate-400 hover:text-slate-200 bg-slate-900/40'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Transcript Body */}
      <div className="flex-1 overflow-y-auto max-h-80 pr-2 space-y-2 text-sm leading-relaxed border border-slate-800/80 rounded-xl bg-slate-900/60 p-4">
        {words.length === 0 ? (
          <p className="text-slate-500 italic">No transcript words available.</p>
        ) : (
          <div className="flex flex-wrap gap-x-1.5 gap-y-2">
            {words.map((w, idx) => {
              const flaw = findFlawForWord(w);
              const isLowConfidence = w.probability < 0.6;
              const isSelected = selectedTime !== null && selectedTime >= w.start && selectedTime <= w.end;

              // Filter logic
              if (filterType === 'flaws' && !flaw) return null;
              if (filterType === 'low-confidence' && !isLowConfidence) return null;

              let badgeClasses = 'text-slate-200 hover:text-white hover:bg-slate-800/60';
              if (flaw) {
                badgeClasses =
                  flaw.severity === 'high'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 font-semibold'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-semibold';
              } else if (isLowConfidence) {
                badgeClasses = 'bg-sky-500/15 text-sky-300 border border-sky-500/30';
              }

              if (isSelected) {
                badgeClasses += ' ring-2 ring-brand-400 bg-brand-500/30 text-white font-bold';
              }

              return (
                <button
                  key={`${w.word}-${w.start}-${idx}`}
                  onClick={() => onWordClick(w.start)}
                  className={`px-2 py-0.5 rounded-md text-xs transition-all duration-150 inline-flex items-center group relative cursor-pointer ${badgeClasses}`}
                  title={`[${w.start}s - ${w.end}s] Confidence: ${Math.round(w.probability * 100)}%${
                    flaw ? ` | Flaw: ${flaw.type} - ${flaw.evidence}` : ''
                  }`}
                >
                  <span>{w.word}</span>

                  {/* Micro timestamp indicator */}
                  <span className="text-[9px] opacity-40 ml-1 group-hover:opacity-100 font-mono">
                    {w.start}s
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center space-x-1">
          <Clock className="w-3 h-3 text-slate-500" />
          <span>Click any word to seek audio to that timestamp.</span>
        </span>
        <span className="font-mono text-slate-500">{words.length} words detected</span>
      </div>
    </div>
  );
}
