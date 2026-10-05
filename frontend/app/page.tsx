"use client";

import React, { useState, useCallback } from "react";
import {
  UploadCloud, FileText, X, Sparkles, Brain, Cpu, Layers, FileCheck2,
  CheckCircle2, AlertTriangle, ArrowRight, RotateCcw, Activity, GraduationCap,
} from "lucide-react";

type Stage = "IDLE" | "FILE_SELECTED" | "ANALYZING" | "SUCCESS" | "ERROR";

interface TopPrediction { category: string; confidence: number }
interface ClassifyResult {
  filename: string;
  predicted_category: string;
  confidence: number;
  top_predictions: TopPrediction[];
  extracted_text_length: number;
  model: string;
}

function ResultView({ result, onReset }: { result: ClassifyResult; onReset: () => void }) {
  return (
    <div className="mt-6 space-y-6">
      <div className="rounded-2xl border border-cyan-500/30 bg-cyan-500/5 p-8 text-center">
        <p className="text-xs uppercase tracking-widest text-cyan-300">Predicted Category</p>
        <p className="mt-2 text-3xl md:text-4xl font-extrabold text-white">{result.predicted_category}</p>
        <div className="mt-5 max-w-md mx-auto">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span>Model Score</span><span>{(result.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="h-3 rounded-full bg-slate-800">
            <div className="h-3 rounded-full bg-gradient-to-r from-cyan-400 to-indigo-500" style={{ width: `${Math.min(result.confidence * 100, 100)}%` }} />
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-500">AI Classification Complete</p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-xs text-slate-500">File</p>
          <p className="text-sm text-slate-200 mt-1 truncate">{result.filename}</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-xs text-slate-500">Extracted Text Length</p>
          <p className="text-sm text-slate-200 mt-1">{result.extracted_text_length.toLocaleString()} chars</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-xs text-slate-500">Processing Status</p>
          <p className="text-sm text-emerald-300 mt-1">Success</p>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h4 className="text-sm font-semibold text-slate-200 mb-4">Top Predictions</h4>
        <div className="space-y-3">
          {result.top_predictions.map((p) => (
            <div key={p.category}>
              <div className="flex justify-between text-xs text-slate-400">
                <span>{p.category}</span><span>{(p.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="h-2 rounded-full bg-slate-800 mt-1">
                <div className="h-2 rounded-full bg-cyan-500/70" style={{ width: `${Math.min(p.confidence * 100, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
        <p className="mt-4 text-[11px] text-slate-600">Scores are relative model decision scores, not calibrated probabilities.</p>
      </div>

      <button onClick={onReset} className="inline-flex items-center gap-2 rounded-xl border border-slate-700 hover:border-slate-500 px-5 py-2.5 text-sm text-slate-300 transition">
        <RotateCcw className="h-4 w-4" /> Analyze another resume
      </button>
    </div>
  );
}

export default function DashboardPage() {
  const [stage, setStage] = useState<Stage>("IDLE");
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<ClassifyResult | null>(null);
  const [error, setError] = useState<string>("");
  const [step, setStep] = useState(0);
  const [isDemo, setIsDemo] = useState(false);

  const pickFile = (f: File | null) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a valid PDF.");
      setStage("ERROR");
      return;
    }
    setFile(f);
    setStage("FILE_SELECTED");
    setError("");
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    pickFile(e.dataTransfer.files?.[0] ?? null);
  }, []);

  const runAnalysis = async (f: File) => {
    setStage("ANALYZING");
    setStep(1);
    const form = new FormData();
    form.append("file", f);
    const t1 = setTimeout(() => setStep(2), 600);
    const t2 = setTimeout(() => setStep(3), 1200);
    try {
      const res = await fetch("/api/classify", { method: "POST", body: form })
        .catch(() => { throw new Error("Unable to connect to the AI service.\nPlease make sure the backend is running."); });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Unexpected server error.");
      if (!data.success) throw new Error(data?.error?.message ?? "Unexpected server error.");
      setResult(data.data);
      setStep(4);
      setStage("SUCCESS");
    } catch (e: any) {
      setError(e.message ?? "Unexpected server error.");
      setStage("ERROR");
    } finally {
      clearTimeout(t1); clearTimeout(t2);
    }
  };

  const tryDemo = async () => {
    setIsDemo(true);
    try {
      const res = await fetch("/sample_resume.pdf");
      const blob = await res.blob();
      const f = new File([blob], "sample_resume.pdf", { type: "application/pdf" });
      setFile(f);
      await runAnalysis(f);
    } catch {
      setError("Demo resume unavailable.");
      setStage("ERROR");
    } finally {
      setIsDemo(false);
    }
  };

  const reset = () => {
    setStage("IDLE"); setFile(null); setResult(null); setError(""); setStep(0);
  };

  const steps = ["Extracting text", "Cleaning resume content", "Running AI classification", "Preparing results"];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-50 border-b border-slate-800/70 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-white">ResumeForge AI</h1>
              <p className="text-xs text-slate-400">AI-Powered Resume Classification</p>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-slate-300">
            <a href="#dashboard" className="hover:text-white">Dashboard</a>
            <a href="#analyze" className="hover:text-white">Analyze Resume</a>
            <a href="#model" className="hover:text-white">About Model</a>
          </nav>
          <div className="flex items-center gap-2 text-xs text-emerald-300 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-3 py-1">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            AI Model Online
          </div>
        </div>
      </header>

      <section id="dashboard" className="max-w-6xl mx-auto px-6 py-14 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <h2 className="text-4xl md:text-5xl font-extrabold leading-tight bg-gradient-to-r from-white to-cyan-200 bg-clip-text text-transparent">
            Turn a Resume into a Career Category — Instantly.
          </h2>
          <p className="mt-4 text-slate-400 text-lg">
            Upload a resume and let ResumeForge AI analyze its content using NLP and machine learning.
          </p>
          <div className="mt-8 flex gap-4">
            <a href="#analyze" className="inline-flex items-center gap-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-6 py-3 transition">
              Analyze Resume <ArrowRight className="h-4 w-4" />
            </a>
            <a href="#model" className="inline-flex items-center gap-2 rounded-xl border border-slate-700 hover:border-slate-500 px-6 py-3 text-slate-300 transition">
              View Model
            </a>
          </div>
        </div>
        <div className="rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-900/40 p-8">
          <div className="flex items-center gap-3 mb-6">
            <Brain className="h-6 w-6 text-cyan-400" />
            <span className="text-sm text-slate-300 font-medium">Neural Classification Pipeline</span>
          </div>
          <div className="space-y-3">
            {["PDF", "Text Extraction", "Preprocessing", "TF-IDF", "Linear SVM", "Prediction"].map((s, i) => (
              <div key={s} className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-cyan-400" style={{ opacity: 1 - i * 0.12 }} />
                <div className="flex-1 h-8 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center px-4 text-sm text-slate-300">{s}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="analyze" className="max-w-6xl mx-auto px-6 pb-16">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-8">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <UploadCloud className="h-5 w-5 text-cyan-400" /> Analyze a Resume
          </h3>

          {stage === "SUCCESS" && result ? (
            <ResultView result={result} onReset={reset} />
          ) : (
            <>
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={onDrop}
                className={`mt-6 rounded-2xl border-2 border-dashed p-12 text-center transition ${isDragging ? "border-cyan-400 bg-cyan-500/5" : "border-slate-700 hover:border-slate-600"}`}
              >
                <UploadCloud className="h-12 w-12 mx-auto text-slate-500" />
                <p className="mt-4 text-slate-200 font-medium">Drop your resume here</p>
                <p className="text-sm text-slate-500 mt-1">or</p>
                <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 px-5 py-2.5 text-sm transition">
                  <FileText className="h-4 w-4" /> Browse PDF
                  <input type="file" accept="application/pdf,.pdf" className="hidden" onChange={(e) => pickFile(e.target.files?.[0] ?? null)} />
                </label>
                <p className="mt-3 text-xs text-slate-500">PDF files only • Maximum recommended size: 10 MB</p>
              </div>

              {file && stage !== "ANALYZING" && (
                <div className="mt-4 flex items-center justify-between rounded-xl border border-slate-700 bg-slate-800/50 px-4 py-3">
                  <div className="flex items-center gap-3">
                    <FileCheck2 className="h-5 w-5 text-cyan-400" />
                    <span className="text-sm text-slate-200">{file.name}</span>
                    <span className="text-xs text-slate-500">{(file.size / 1024).toFixed(0)} KB</span>
                  </div>
                  <button onClick={reset} aria-label="Remove file" className="text-slate-500 hover:text-white">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}

              {stage === "ANALYZING" && (
                <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
                  <p className="text-slate-200 font-medium mb-4">Analyzing Resume…</p>
                  <ul className="space-y-2">
                    {steps.map((s, i) => (
                      <li key={s} className="flex items-center gap-3 text-sm">
                        {step > i + 1 ? <CheckCircle2 className="h-4 w-4 text-emerald-400" /> :
                         step === i + 1 ? <span className="h-4 w-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" /> :
                         <span className="h-4 w-4 rounded-full border-2 border-slate-700" />}
                        <span className={step > i ? "text-slate-200" : "text-slate-600"}>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {stage === "ERROR" && (
                <div className="mt-4 flex items-start gap-3 rounded-xl border border-rose-500/40 bg-rose-500/10 p-4">
                  <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0" />
                  <p className="text-sm text-rose-200 whitespace-pre-line">{error}</p>
                </div>
              )}

              <div className="mt-6 flex flex-wrap gap-4">
                <button
                  disabled={!file || stage === "ANALYZING"}
                  onClick={() => file && runAnalysis(file)}
                  className="inline-flex items-center gap-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 font-semibold px-6 py-3 transition"
                >
                  <Activity className="h-4 w-4" /> Analyze
                </button>
                <button
                  disabled={stage === "ANALYZING" || isDemo}
                  onClick={tryDemo}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-700 hover:border-slate-500 px-6 py-3 text-slate-300 transition disabled:opacity-40"
                >
                  <Sparkles className="h-4 w-4" /> {isDemo ? "Loading demo…" : "Try Demo Resume"}
                </button>
              </div>
            </>
          )}
        </div>
      </section>

      <section id="model" className="max-w-6xl mx-auto px-6 pb-20 grid md:grid-cols-2 gap-8">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-8">
          <h3 className="text-lg font-bold flex items-center gap-2"><Cpu className="h-5 w-5 text-cyan-400" /> Powered by Machine Learning</h3>
          <dl className="mt-6 grid grid-cols-2 gap-y-3 text-sm">
            <dt className="text-slate-500">Model</dt><dd className="text-slate-200 font-medium">Linear SVM</dd>
            <dt className="text-slate-500">Features</dt><dd className="text-slate-200 font-medium">Word TF-IDF + Character TF-IDF</dd>
            <dt className="text-slate-500">Categories</dt><dd className="text-slate-200 font-medium">24</dd>
            <dt className="text-slate-500">Training Resumes</dt><dd className="text-slate-200 font-medium">2,500</dd>
            <dt className="text-slate-500">Test Accuracy</dt><dd className="text-emerald-300 font-semibold">70.24%</dd>
            <dt className="text-slate-500">Macro-F1</dt><dd className="text-emerald-300 font-semibold">68.18%</dd>
            <dt className="text-slate-500">Weighted-F1</dt><dd className="text-emerald-300 font-semibold">69.29%</dd>
          </dl>
        </div>
        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-8">
          <h3 className="text-lg font-bold flex items-center gap-2"><Layers className="h-5 w-5 text-cyan-400" /> Model Comparison</h3>
          <table className="mt-6 w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-left border-b border-slate-800">
                <th className="pb-2">Model</th><th className="pb-2 text-right">Accuracy</th><th className="pb-2 text-right">Macro-F1</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800/60">
                <td className="py-2 text-slate-300">Logistic Regression</td>
                <td className="py-2 text-right text-slate-400">67.02%</td>
                <td className="py-2 text-right text-slate-400">62.24%</td>
              </tr>
              <tr>
                <td className="py-2 text-cyan-300 font-semibold">Linear SVM <span className="ml-2 text-[10px] uppercase tracking-wider bg-cyan-500/10 border border-cyan-500/30 rounded-full px-2 py-0.5">Selected</span></td>
                <td className="py-2 text-right text-cyan-300 font-semibold">70.24%</td>
                <td className="py-2 text-right text-cyan-300 font-semibold">68.18%</td>
              </tr>
            </tbody>
          </table>
          <p className="mt-4 text-xs text-slate-500 flex items-center gap-1">
            <GraduationCap className="h-3 w-3" /> Resume Insights (skills, education) extraction — Coming Soon
          </p>
        </div>
      </section>
    </main>
  );
}
