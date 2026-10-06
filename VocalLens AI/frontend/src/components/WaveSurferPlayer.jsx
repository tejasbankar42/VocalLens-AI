import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, RotateCcw, Volume2, AlertCircle, AlertTriangle } from 'lucide-react';

export default function WaveSurferPlayer({
  audioUrl,
  flawEvents = [],
  duration = 0,
  activeFlaw = null,
  onFlawClick = () => {},
  seekTrigger = null,
}) {
  const containerRef = useRef(null);
  const wavesurfer = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [totalDuration, setTotalDuration] = useState(duration || 0);

  useEffect(() => {
    if (!containerRef.current) return;

    // Destroy existing instance if any
    if (wavesurfer.current) {
      wavesurfer.current.destroy();
    }

    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#334155',
      progressColor: '#14b8a6',
      cursorColor: '#2dd4bf',
      barWidth: 3,
      barRadius: 3,
      barGap: 2,
      height: 72,
      normalize: true,
      backend: 'WebAudio',
    });

    wavesurfer.current = ws;

    // Load audio URL (fallback to synthetic waveform if URL is mock)
    if (audioUrl) {
      ws.load(audioUrl);
    }

    ws.on('ready', () => {
      const dur = ws.getDuration();
      setTotalDuration(dur || duration);
    });

    ws.on('audioprocess', () => {
      setCurrentTime(ws.getCurrentTime());
    });

    ws.on('seeking', () => {
      setCurrentTime(ws.getCurrentTime());
    });

    ws.on('play', () => setIsPlaying(true));
    ws.on('pause', () => setIsPlaying(false));
    ws.on('finish', () => {
      setIsPlaying(false);
      setCurrentTime(0);
    });

    return () => {
      ws.destroy();
    };
  }, [audioUrl]);

  // Handle external seek triggers
  useEffect(() => {
    if (seekTrigger !== null && wavesurfer.current && totalDuration > 0) {
      const targetSec = Math.max(0, Math.min(totalDuration, seekTrigger));
      const progress = targetSec / totalDuration;
      wavesurfer.current.seekTo(progress);
      wavesurfer.current.play();
    }
  }, [seekTrigger, totalDuration]);

  const togglePlay = () => {
    if (wavesurfer.current) {
      wavesurfer.current.playPause();
    }
  };

  const handleRestart = () => {
    if (wavesurfer.current) {
      wavesurfer.current.seekTo(0);
      wavesurfer.current.play();
    }
  };

  const jumpToSecond = (sec) => {
    if (wavesurfer.current && totalDuration > 0) {
      const progress = sec / totalDuration;
      wavesurfer.current.seekTo(progress);
      wavesurfer.current.play();
    }
    onFlawClick(sec);
  };

  const formatTime = (time) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="p-6 rounded-2xl glass-panel relative">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Volume2 className="w-4 h-4 text-brand-400" />
          <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-300">
            Temporal Audio Waveform & Flaw Grounding
          </h3>
        </div>
        <div className="text-xs font-mono font-medium text-slate-400">
          <span className="text-brand-300 font-bold">{formatTime(currentTime)}</span> / {formatTime(totalDuration)}
        </div>
      </div>

      {/* Waveform Container */}
      <div className="relative w-full rounded-xl bg-slate-900/80 p-3 border border-slate-800/80 overflow-hidden">
        <div ref={containerRef} className="w-full cursor-pointer" />

        {/* Timeline Flaw Markers Overlay */}
        {totalDuration > 0 && flawEvents.length > 0 && (
          <div className="relative w-full h-7 mt-2 border-t border-slate-800">
            {flawEvents.map((flaw, idx) => {
              const leftPercent = (flaw.start / totalDuration) * 100;
              const widthPercent = Math.max(1.8, ((flaw.end - flaw.start) / totalDuration) * 100);
              const isHigh = flaw.severity === 'high';
              const isSelected = activeFlaw && Math.abs(activeFlaw.start - flaw.start) < 0.1;

              return (
                <button
                  key={`${flaw.type}-${flaw.start}-${idx}`}
                  onClick={() => jumpToSecond(flaw.start)}
                  style={{ left: `${leftPercent}%`, width: `${widthPercent}%` }}
                  className={`absolute top-1 h-5 rounded transition-all duration-150 transform hover:scale-110 flex items-center justify-center group ${
                    isHigh
                      ? 'bg-rose-500/80 hover:bg-rose-400 text-white'
                      : 'bg-amber-500/80 hover:bg-amber-400 text-slate-950'
                  } ${isSelected ? 'ring-2 ring-white scale-110 z-20' : 'z-10'}`}
                  title={`${flaw.type.toUpperCase()} (${flaw.start}s - ${flaw.end}s): ${flaw.evidence}`}
                >
                  <span className="text-[9px] font-bold tracking-tighter truncate px-0.5">
                    {flaw.type === 'long_pause' ? 'PAUSE' : flaw.type.toUpperCase().slice(0, 5)}
                  </span>

                  {/* Tooltip on hover */}
                  <span className="absolute bottom-full mb-1 hidden group-hover:flex flex-col items-center z-30 pointer-events-none">
                    <span className="bg-slate-900 text-white text-[10px] rounded px-2 py-1 shadow-2xl border border-slate-700 whitespace-nowrap">
                      <strong className={isHigh ? 'text-rose-400' : 'text-amber-400'}>{flaw.type}</strong> ({flaw.start}s): {flaw.evidence}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Playback Controls & Flaw Legend */}
      <div className="flex flex-wrap items-center justify-between gap-3 mt-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={togglePlay}
            className="w-10 h-10 rounded-xl bg-brand-500 hover:bg-brand-400 text-slate-950 flex items-center justify-center shadow-lg shadow-brand-500/20 font-bold transition-all"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
          </button>
          <button
            onClick={handleRestart}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Restart playback"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-4 text-xs text-slate-400">
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
            <span>High Flaw ({flawEvents.filter(f => f.severity === 'high').length})</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
            <span>Medium Flaw ({flawEvents.filter(f => f.severity !== 'high').length})</span>
          </span>
        </div>
      </div>
    </div>
  );
}
