import React, { useEffect, useState } from 'react';
import { Database, Play, Volume2, ShieldCheck, CheckCircle2, AlertTriangle, Layers, Percent } from 'lucide-react';
import { fetchBaseline } from '../api/client';

export default function DatasetInsightsPage() {
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

  const weights = baseline?.weights || {
    clarity: 15.0,
    fluency: 15.0,
    pace: 15.0,
    pauses: 15.0,
    fillers: 15.0,
    pronunciation: 10.0,
    confidence: 10.0,
    vocabulary: 5.0,
  };

  const samplePairs = [
    {
      id: '01',
      title: 'Tech Interview Introduction',
      idealAudio: '/dataset_audio/ideal/ideal_01_sample_01_interview.wav',
      flawedAudio: '/dataset_audio/flawed/flawed_01_sample_01_interview.wav',
      idealDesc: 'Balanced cadence (142 WPM), crisp articulation, zero fillers.',
      flawedDesc: '2.2s dead pauses, repeated words ("we we"), "basically/like" verbal crutches.',
    },
    {
      id: '02',
      title: 'AI Product Pitch',
      idealAudio: '/dataset_audio/ideal/ideal_02_sample_02_pitch.wav',
      flawedAudio: '/dataset_audio/flawed/flawed_02_sample_02_pitch.wav',
      idealDesc: 'Persuasive pitch rhythm, clear value propositions, dynamic prosody.',
      flawedDesc: '2.5s awkward pause, fillers ("um", "matlab"), stuttered repetition ("because because").',
    },
    {
      id: '03',
      title: 'Executive Milestone Review',
      idealAudio: '/dataset_audio/ideal/ideal_03_sample_03_leadership.wav',
      flawedAudio: '/dataset_audio/flawed/flawed_03_sample_03_leadership.wav',
      idealDesc: 'Commanding tone, confident milestone articulation, steady pacing.',
      flawedDesc: 'Prolonged hesitation gap, low pitch variety, hedging phrasing.',
    },
    {
      id: '04',
      title: 'Customer Escalation Support',
      idealAudio: '/dataset_audio/ideal/ideal_04_sample_04_support.wav',
      flawedAudio: '/dataset_audio/flawed/flawed_04_sample_04_support.wav',
      idealDesc: 'Reassuring resolution delivery, empathetic inflection, clear solution steps.',
      flawedDesc: '2.3s silence, disfluent restarts, "toh/basically" verbal crutches.',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="pb-6 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20">
            Dataset Architecture
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1.5">
          Contrastive Dataset & Calibration Distributions
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Explore the calibrated distributions and paired audio corpus powering VocalLens AI's reproducible rubric scoring.
        </p>
      </div>

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-panel">
          <span className="text-xs font-semibold uppercase text-slate-400">Contrastive Separation</span>
          <div className="my-2">
            <span className="text-3xl font-black text-emerald-400">+68.0</span>
            <span className="text-xs text-slate-400 ml-1">pts</span>
          </div>
          <p className="text-[11px] text-slate-400">Average Ideal (85.9) vs Flawed (17.8)</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel">
          <span className="text-xs font-semibold uppercase text-slate-400">Speech Dimensions</span>
          <div className="my-2">
            <span className="text-3xl font-black text-brand-300">8</span>
          </div>
          <p className="text-[11px] text-slate-400">Totaling exactly 100% weight</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel">
          <span className="text-xs font-semibold uppercase text-slate-400">Corpus Calibration</span>
          <div className="my-2">
            <span className="text-3xl font-black text-cyan-400">Paired</span>
          </div>
          <p className="text-[11px] text-slate-400">Identical scripts in Ideal vs Flawed styles</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel">
          <span className="text-xs font-semibold uppercase text-slate-400">Determinism Level</span>
          <div className="my-2">
            <span className="text-3xl font-black text-emerald-400">100%</span>
          </div>
          <p className="text-[11px] text-slate-400">Zero LLM stochastic variance</p>
        </div>
      </div>

      {/* Rubric Weights & Bands Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Dimension Weights */}
        <div className="md:col-span-7 p-6 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
              Deterministic Rubric Weights
            </h3>
            <span className="text-xs text-brand-300 font-mono font-bold">Sum = 100%</span>
          </div>

          <div className="space-y-3">
            {Object.entries(weights).map(([dim, wt]) => (
              <div key={dim} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="capitalize text-slate-200 font-medium">{dim}</span>
                  <span className="font-mono text-brand-300 font-bold">{wt}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-brand-500 to-cyan-400 rounded-full"
                    style={{ width: `${(wt / 20) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Score Bands */}
        <div className="md:col-span-5 p-6 rounded-2xl glass-panel flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300 mb-4">
              Calibrated Performance Bands
            </h3>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                <div className="flex justify-between font-bold text-emerald-300">
                  <span>Excellent</span>
                  <span>85 – 100 pts</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Professional, engaging, near-zero filler speech.</p>
              </div>

              <div className="p-3 rounded-xl bg-teal-500/10 border border-teal-500/30">
                <div className="flex justify-between font-bold text-teal-300">
                  <span>Good</span>
                  <span>70 – 84.9 pts</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Clear structure with minor hesitations or pacing drift.</p>
              </div>

              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30">
                <div className="flex justify-between font-bold text-amber-300">
                  <span>Needs Work</span>
                  <span>50 – 69.9 pts</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Noticeable pause clusters, repetitive words, or fillers.</p>
              </div>

              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30">
                <div className="flex justify-between font-bold text-rose-300">
                  <span>Weak</span>
                  <span>0 – 49.9 pts</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Frequent disfluency, prolonged silence, or monotone pitch.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Paired Contrastive Audio Samples Audio Players */}
      <div className="p-6 rounded-2xl glass-panel space-y-6">
        <div>
          <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
            Interactive Audio Exemplar Gallery
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Listen directly to the paired ideal vs. flawed audio files from the benchmark dataset.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {samplePairs.map((pair) => (
            <div key={pair.id} className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
              <h4 className="text-sm font-bold text-white flex items-center justify-between">
                <span>{pair.title}</span>
                <span className="text-[10px] font-mono text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20">
                  Sample {pair.id}
                </span>
              </h4>

              {/* Ideal Audio */}
              <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 space-y-1.5">
                <div className="flex items-center justify-between text-xs text-emerald-300 font-semibold">
                  <span className="flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Ideal Exemplar</span>
                  </span>
                  <span className="text-[10px] text-emerald-400/80 font-mono">155 WPM • 0 Fillers</span>
                </div>
                <p className="text-[11px] text-slate-400">{pair.idealDesc}</p>
                <audio src={pair.idealAudio} controls className="w-full h-8 mt-1" />
              </div>

              {/* Flawed Audio */}
              <div className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/20 space-y-1.5">
                <div className="flex items-center justify-between text-xs text-rose-300 font-semibold">
                  <span className="flex items-center space-x-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Flawed Speech Sample</span>
                  </span>
                  <span className="text-[10px] text-rose-400/80 font-mono">Pauses & Fillers Grounded</span>
                </div>
                <p className="text-[11px] text-slate-400">{pair.flawedDesc}</p>
                <audio src={pair.flawedAudio} controls className="w-full h-8 mt-1" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
