import React, { useState } from 'react';
import {
  Award,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Layers,
  ArrowRight,
  Sparkles,
  Zap,
} from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import RadarChartComponent from '../components/RadarChartComponent';
import WaveSurferPlayer from '../components/WaveSurferPlayer';
import TranscriptViewer from '../components/TranscriptViewer';
import FeedbackCard from '../components/FeedbackCard';
import MetricCard from '../components/MetricCard';

export default function ReportPage({ report, onNavigateToCompare, onNavigateToRecord }) {
  const [seekTime, setSeekTime] = useState(null);
  const [selectedFlaw, setSelectedFlaw] = useState(null);
  const [flawFilter, setFlawFilter] = useState('all');

  if (!report) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
          <Layers className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-white">No Report Available Yet</h2>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Record your speech or run a sample session to generate an in-depth contrastive evaluation.
        </p>
        <button
          onClick={onNavigateToRecord}
          className="px-6 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-400 text-slate-950 font-bold text-xs shadow-lg shadow-brand-500/20"
        >
          Start Speech Recording
        </button>
      </div>
    );
  }

  const {
    overall_score = 0,
    band = 'Needs work',
    dimension_scores = {},
    strengths = [],
    weaknesses = [],
    duration = 0,
    wpm = 0,
    pause_count = 0,
    filler_count = 0,
    flaw_events = [],
    transcript_text = '',
    transcript_words = [],
    feedback_tips = [],
    raw_metrics = {},
    filename = 'recording.wav',
  } = report;

  // Filter flaw events
  const filteredFlaws = flawFilter === 'all'
    ? flaw_events
    : flaw_events.filter((f) => f.type === flawFilter);

  const handleWordOrFlawClick = (timestampSec) => {
    setSeekTime(timestampSec);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Report Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20">
              Evaluation Report
            </span>
            <span className="text-xs text-slate-500 font-mono">
              ID: {report.session_id ? report.session_id.slice(0, 8) : 'demo'}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1.5">
            Speech Diagnostic & Temporal Flaw Grounding
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Source: <span className="text-slate-300 font-medium">{filename}</span> ({duration} seconds)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onNavigateToCompare}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-brand-300 border border-brand-500/30 text-xs font-semibold shadow-sm transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>Contrast with Exemplars</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </button>
        </div>
      </div>

      {/* Row 1: High Level Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          title="Cadence (WPM)"
          value={wpm}
          unit="words/min"
          subtext={wpm >= 130 && wpm <= 155 ? 'Optimal conversational target' : 'Outside 130–155 target'}
          icon={Clock}
        />
        <MetricCard
          title="Hesitation Pauses"
          value={pause_count}
          unit="events"
          subtext="Gaps > 1.2s between words"
          icon={AlertTriangle}
        />
        <MetricCard
          title="Filler Count"
          value={filler_count}
          unit="vocalizations"
          subtext="um, uh, like, basically, etc."
          icon={Zap}
        />
        <MetricCard
          title="Total Duration"
          value={duration}
          unit="seconds"
          subtext="Processed speech stream"
          icon={TrendingUp}
        />
      </div>

      {/* Row 2: Score Gauge + Radar Chart + Strengths & Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Score Gauge */}
        <div className="lg:col-span-4">
          <ScoreGauge score={overall_score} band={band} />
        </div>

        {/* 8-Dimension Radar */}
        <div className="lg:col-span-5">
          <RadarChartComponent dimensionScores={dimension_scores} />
        </div>

        {/* Strengths & Weaknesses Panel */}
        <div className="lg:col-span-3 p-6 rounded-2xl glass-panel flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-400 mb-3">
              Performance Highlights
            </h3>

            {/* Strengths */}
            <div className="space-y-2 mb-4">
              <span className="text-xs font-bold text-emerald-400 flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Strongest Areas</span>
              </span>
              <div className="flex flex-wrap gap-1.5">
                {strengths.length > 0 ? (
                  strengths.map((s) => (
                    <span
                      key={s}
                      className="px-2.5 py-1 rounded-md bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs capitalize font-medium"
                    >
                      {s} ({dimension_scores[s] || 85} pts)
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400 italic">None highlighted</span>
                )}
              </div>
            </div>

            {/* Weaknesses */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-rose-400 flex items-center space-x-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Priority Improvement</span>
              </span>
              <div className="flex flex-wrap gap-1.5">
                {weaknesses.length > 0 ? (
                  weaknesses.map((w) => (
                    <span
                      key={w}
                      className="px-2.5 py-1 rounded-md bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs capitalize font-medium"
                    >
                      {w} ({dimension_scores[w] || 50} pts)
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400 italic">No critical weak areas</span>
                )}
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400">
            Weighted across 8 contrastive dimensions.
          </div>
        </div>
      </div>

      {/* Row 3: WaveSurfer Player with Flaw Pins */}
      <div>
        <WaveSurferPlayer
          audioUrl={report.audio_path || '/audio/demo_flagship.wav'}
          flawEvents={flaw_events}
          duration={duration}
          activeFlaw={selectedFlaw}
          onFlawClick={handleWordOrFlawClick}
          seekTrigger={seekTime}
        />
      </div>

      {/* Row 4: Interactive Transcript & Temporal Flaws List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Transcript Viewer */}
        <div className="lg:col-span-7">
          <TranscriptViewer
            words={transcript_words}
            flawEvents={flaw_events}
            onWordClick={handleWordOrFlawClick}
            selectedTime={seekTime}
          />
        </div>

        {/* Timestamped Flaws List */}
        <div className="lg:col-span-5 p-6 rounded-2xl glass-panel flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
              Grounded Flaws ({flaw_events.length})
            </h3>

            {/* Flaw Type Selector */}
            <select
              value={flawFilter}
              onChange={(e) => setFlawFilter(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-md px-2 py-1 text-[11px] text-slate-300"
            >
              <option value="all">All Types</option>
              <option value="long_pause">Long Pauses</option>
              <option value="filler">Fillers</option>
              <option value="repetition">Repetitions</option>
              <option value="too_fast">Pacing Spikes</option>
              <option value="mumble">Mumbling</option>
              <option value="monotone">Monotone Pitch</option>
            </select>
          </div>

          <div className="flex-1 overflow-y-auto max-h-80 space-y-2 pr-1">
            {filteredFlaws.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center text-xs text-slate-400">
                No flaws detected in this category. Excellent delivery!
              </div>
            ) : (
              filteredFlaws.map((flaw, idx) => {
                const isHigh = flaw.severity === 'high';
                return (
                  <div
                    key={`${flaw.type}-${flaw.start}-${idx}`}
                    onClick={() => {
                      setSelectedFlaw(flaw);
                      handleWordOrFlawClick(flaw.start);
                    }}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col space-y-1 ${
                      isHigh
                        ? 'bg-rose-500/10 border-rose-500/20 hover:border-rose-500/50'
                        : 'bg-amber-500/10 border-amber-500/20 hover:border-amber-500/50'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-slate-100 flex items-center space-x-1.5">
                        <span className={`w-2 h-2 rounded-full ${isHigh ? 'bg-rose-500' : 'bg-amber-500'}`} />
                        <span className="capitalize">{flaw.type.replace('_', ' ')}</span>
                      </span>
                      <span className="font-mono text-[11px] text-brand-300 font-semibold">
                        {flaw.start}s – {flaw.end}s
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-snug">{flaw.evidence}</p>
                    <p className="text-[11px] text-slate-400 italic pt-1">{flaw.tip}</p>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Row 5: Actionable Feedback Coaching Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Actionable Improvement Coaching</h2>
            <p className="text-xs text-slate-400">
              Rubric-based tactical drills tailored to your weakest dimensions and detected flaws.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {feedback_tips.map((tip, idx) => (
            <FeedbackCard key={`${tip.dimension}-${idx}`} tip={tip} />
          ))}
        </div>
      </div>
    </div>
  );
}
