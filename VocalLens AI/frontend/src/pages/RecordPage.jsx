import React, { useState, useRef, useEffect } from 'react';
import {
  Mic,
  Square,
  Upload,
  Globe,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Clock,
  AudioWaveform,
  Play,
  FileAudio,
} from 'lucide-react';
import { analyzeAudio } from '../api/client';

export default function RecordPage({ onAnalysisComplete, onSelectDemo }) {
  // State
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [language, setLanguage] = useState('en');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Refs for recording & Web Audio API
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const fileInputRef = useRef(null);

  // Clean up timer and audio context on unmount
  useEffect(() => {
    return () => {
      clearInterval(timerIntervalRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (audioContextRef.current) audioContextRef.current.close().catch(() => {});
    };
  }, []);

  // Live Waveform Visualizer
  const startCanvasVisualizer = (stream) => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const ctx = new AudioContext();
    audioContextRef.current = ctx;

    const source = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);
    analyserRef.current = analyser;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const canvasCtx = canvas.getContext('2d');
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);

      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
      const barWidth = (canvas.width / bufferLength) * 1.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height * 0.9;
        
        // Gradient color from teal to cyan
        const grad = canvasCtx.createLinearGradient(0, canvas.height, 0, 0);
        grad.addColorStop(0, '#0d9488');
        grad.addColorStop(1, '#2dd4bf');

        canvasCtx.fillStyle = grad;
        canvasCtx.fillRect(x, (canvas.height - barHeight) / 2, barWidth - 1, barHeight);
        x += barWidth;
      }
    };
    draw();
  };

  // Start Mic Recording
  const startRecording = async () => {
    setErrorMessage('');
    setAudioBlob(null);
    setAudioUrl(null);
    setSelectedFile(null);
    setRecordingSeconds(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      startCanvasVisualizer(stream);

      const mimeType = MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : MediaRecorder.isTypeSupported('audio/ogg')
        ? 'audio/ogg'
        : 'audio/wav';

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((track) => track.stop());
        if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
        if (audioContextRef.current) audioContextRef.current.close().catch(() => {});
      };

      mediaRecorder.start(250); // collect chunks every 250ms
      setIsRecording(true);

      timerIntervalRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      setErrorMessage(
        'Microphone access was denied or not found. Please verify browser microphone permissions or upload an audio file below.'
      );
    }
  };

  // Stop Mic Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerIntervalRef.current);
    }
  };

  // Handle File Upload
  const handleFileChange = (e) => {
    setErrorMessage('');
    const file = e.target.files[0];
    if (!file) return;

    // Check size (< 50MB)
    if (file.size > 50 * 1024 * 1024) {
      setErrorMessage('Audio file size exceeds the 50MB limit.');
      return;
    }

    setSelectedFile(file);
    setAudioBlob(file);
    setAudioUrl(URL.createObjectURL(file));
  };

  // Run Analysis Pipeline with Progress Animation
  const handleAnalyze = async () => {
    const fileToAnalyze = selectedFile || audioBlob;
    if (!fileToAnalyze) {
      setErrorMessage('Please record your voice or select an audio file first.');
      return;
    }

    if (recordingSeconds > 0 && recordingSeconds < 5) {
      setErrorMessage('Audio is too short (must be at least 5.0 seconds of speech for accurate contrastive evaluation).');
      return;
    }

    setErrorMessage('');
    setIsAnalyzing(true);

    const steps = [
      'Uploading audio to secure processing pipeline...',
      'Running faster-whisper ASR & word timestamp alignment...',
      'Extracting acoustic prosody, pitch dynamics & RMS energy...',
      'Contrasting speech dimensions against ideal & flawed benchmarks...',
      'Grounding temporal flaw markers & synthesizing actionable feedback...',
    ];

    let stepIdx = 0;
    setAnalysisStep(steps[0]);
    const stepInterval = setInterval(() => {
      stepIdx++;
      if (stepIdx < steps.length) {
        setAnalysisStep(steps[stepIdx]);
      }
    }, 1800);

    try {
      const report = await analyzeAudio(fileToAnalyze, language);
      clearInterval(stepInterval);
      setIsAnalyzing(false);
      onAnalysisComplete(report);
    } catch (err) {
      clearInterval(stepInterval);
      setIsAnalyzing(false);
      setErrorMessage(err.message || 'Analysis failed. Please try again.');
    }
  };

  const formatTime = (secs) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${rem.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Hero Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-brand-400" />
          <span>Contrastive Speech Analytics & Temporal Flaw Grounding</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
          Speak with Confidence. <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-brand-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
            Measure Every Dimension.
          </span>
        </h1>
        <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
          Record or upload your speech. VocalLens AI compares your cadence against verified ideal exemplars,
          pointing out exact timestamped flaws on your audio timeline.
        </p>
      </div>

      {/* Quick Judge Showcase Banner */}
      <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/5 backdrop-blur flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2 text-amber-300">
          <Sparkles className="w-4 h-4 flex-shrink-0" />
          <span>
            <strong>Judging or demoing?</strong> Load a pre-analyzed session immediately without recording:
          </span>
        </div>
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <button
            onClick={() => onSelectDemo('flagship')}
            className="flex-1 sm:flex-none px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 font-medium transition-colors"
          >
            Ideal Session (89.5)
          </button>
          <button
            onClick={() => onSelectDemo('flawed')}
            className="flex-1 sm:flex-none px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 font-medium transition-colors"
          >
            Flawed Session (51.8)
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start space-x-2 animate-in fade-in">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Main Recording / Upload Card */}
      <div className="p-6 sm:p-8 rounded-2xl glass-panel space-y-6">
        {/* Language & Settings Toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Globe className="w-4 h-4 text-brand-400" />
            <label htmlFor="languageSelect" className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Speech Language
            </label>
          </div>
          <select
            id="languageSelect"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isRecording || isAnalyzing}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-400"
          >
            <option value="en">English (Global / Standard)</option>
            <option value="hinglish">Hinglish / Indian English (with matlab/toh support)</option>
            <option value="hi">Hindi (Devanagari)</option>
          </select>
        </div>

        {/* Live Audio Visualizer Canvas or Upload Preview */}
        <div className="relative w-full h-36 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col items-center justify-center overflow-hidden">
          {isRecording ? (
            <>
              <canvas ref={canvasRef} width={600} height={140} className="w-full h-full" />
              <div className="absolute top-3 right-3 flex items-center space-x-2 px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-mono font-bold animate-pulse">
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                <span>REC {formatTime(recordingSeconds)}</span>
              </div>
            </>
          ) : audioUrl ? (
            <div className="flex flex-col items-center space-y-2 p-4 text-center">
              <div className="w-12 h-12 rounded-full bg-brand-500/20 text-brand-400 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold text-slate-200">
                Audio Ready for Analysis ({selectedFile ? selectedFile.name : `Recording (${formatTime(recordingSeconds)})`})
              </span>
              <audio src={audioUrl} controls className="h-8 max-w-xs mt-1" />
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-2 text-slate-500">
              <AudioWaveform className="w-10 h-10 stroke-[1.2]" />
              <span className="text-xs">Click record below or drag and drop an audio file</span>
            </div>
          )}
        </div>

        {/* Controls: Record Button & File Upload */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Record Control */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center space-y-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Microphone Capture
            </span>
            {isRecording ? (
              <button
                onClick={stopRecording}
                className="w-16 h-16 rounded-full bg-rose-600 hover:bg-rose-500 text-white flex items-center justify-center shadow-lg shadow-rose-600/30 font-bold transition-all glow-recording transform hover:scale-105"
                title="Stop recording"
              >
                <Square className="w-6 h-6 fill-current" />
              </button>
            ) : (
              <button
                onClick={startRecording}
                disabled={isAnalyzing}
                className="w-16 h-16 rounded-full bg-brand-500 hover:bg-brand-400 text-slate-950 flex items-center justify-center shadow-lg shadow-brand-500/30 font-bold transition-all glow-teal transform hover:scale-105 disabled:opacity-50"
                title="Start recording"
              >
                <Mic className="w-7 h-7" />
              </button>
            )}
            <span className="text-[11px] text-slate-400">
              {isRecording ? 'Click to finish recording (> 5s required)' : 'Speak naturally for 15–45 seconds'}
            </span>
          </div>

          {/* File Upload Control */}
          <div
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
            className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 border-dashed hover:border-brand-500/50 cursor-pointer flex flex-col items-center justify-center space-y-3 transition-colors"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Upload Audio File
            </span>
            <div className="w-16 h-16 rounded-full bg-slate-800 hover:bg-slate-700 text-brand-400 flex items-center justify-center transition-colors">
              <Upload className="w-6 h-6" />
            </div>
            <span className="text-[11px] text-slate-400 text-center">
              WAV, MP3, M4A, WEBM, or OGG up to 50MB
            </span>
          </div>
        </div>

        {/* Primary Action Button */}
        <div className="pt-2">
          <button
            onClick={handleAnalyze}
            disabled={(!audioBlob && !selectedFile) || isRecording || isAnalyzing}
            className={`w-full py-4 rounded-xl font-bold text-sm tracking-wide shadow-xl transition-all duration-200 flex items-center justify-center space-x-2 ${
              isAnalyzing
                ? 'bg-brand-600 text-white cursor-wait'
                : !audioBlob && !selectedFile
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-brand-500 via-teal-400 to-cyan-500 text-slate-950 hover:brightness-110 glow-teal'
            }`}
          >
            {isAnalyzing ? (
              <div className="flex items-center space-x-3">
                <div className="w-5 h-5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>{analysisStep}</span>
              </div>
            ) : (
              <>
                <Sparkles className="w-4 h-4 fill-current" />
                <span>ANALYZE SPEECH & GROUND FLAWS</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
