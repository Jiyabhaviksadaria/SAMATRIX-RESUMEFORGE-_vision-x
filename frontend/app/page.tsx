"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import HackathonWizard from "@/components/HackathonWizard";
import DatasetProfiler from "@/components/DatasetProfiler";
import ModelBenchmark from "@/components/ModelBenchmark";
import ResumeAnalyzer from "@/components/ResumeAnalyzer";
import JobMatcher from "@/components/JobMatcher";
import CandidateRanker from "@/components/CandidateRanker";
import { Sparkles, Brain, Cpu, Layers, GitCompare, Award, CheckCircle2 } from "lucide-react";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<"profiler" | "analyzer" | "matcher" | "ranker">("profiler");
  const [profileData, setProfileData] = useState<any>(null);
  const [metricsData, setMetricsData] = useState<any>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [matchResult, setMatchResult] = useState<any>(null);
  const [rankings, setRankings] = useState<any[]>([]);
  const [predictionResult, setPredictionResult] = useState<any>(null);

  const [isLoadingDemo, setIsLoadingDemo] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isMatching, setIsMatching] = useState(false);
  const [isRanking, setIsRanking] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);

  const API_BASE = "http://localhost:8000";

  // Fetch metrics on mount
  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/metrics`);
      const data = await res.json();
      if (data.success) {
        setMetricsData(data.data);
      }
    } catch (e) {
      console.warn("Backend API offline or loading locally:", e);
    }
  };

  const handleLoadDemo = async () => {
    setIsLoadingDemo(true);
    try {
      const res = await fetch(`${API_BASE}/demo/load`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        // Fetch fresh profile and metrics
        const pRes = await fetch(`${API_BASE}/dataset/profile`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_path: "data/sample/sample_resumes.csv", target_column: "job_role" }),
        });
        const pData = await pRes.json();
        if (pData.success) setProfileData(pData.data);
        await fetchMetrics();
      }
    } catch (e) {
      alert("Failed to connect to FastAPI backend at http://localhost:8000. Ensure backend is running!");
    } finally {
      setIsLoadingDemo(false);
    }
  };

  const handleUploadDataset = async (file: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/dataset/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.success) {
        setProfileData(data.data.profile);
        alert(`Dataset '${file.name}' successfully uploaded & profiled!`);
      } else {
        alert(`Upload error: ${data.error?.message}`);
      }
    } catch (e) {
      alert("Error uploading dataset.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleTrainPipeline = async (targetCol: string, textCols: string[], taskType: string) => {
    setIsTraining(true);
    try {
      const res = await fetch(`${API_BASE}/train`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_column: targetCol, text_columns: textCols, task_type: taskType }),
      });
      const data = await res.json();
      if (data.success) {
        await fetchMetrics();
        alert(`Pipeline successfully trained! Best Model: ${data.data.model}`);
      } else {
        alert(`Training failed: ${data.error?.message}`);
      }
    } catch (e) {
      alert("Training connection error.");
    } finally {
      setIsTraining(false);
    }
  };

  const handleAnalyzeResume = async (text: string, candidateName: string) => {
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append("text", text);
      formData.append("candidate_name", candidateName);

      const res = await fetch(`${API_BASE}/analyze-resume`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.success) {
        setAnalysisResult(data.data);
      }
    } catch (e) {
      alert("Analysis error.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleMatchJob = async (resumeText: string, jobDescription: string) => {
    setIsMatching(true);
    try {
      const res = await fetch(`${API_BASE}/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
      });
      const data = await res.json();
      if (data.success) {
        setMatchResult(data.data);
      }
    } catch (e) {
      alert("Matching error.");
    } finally {
      setIsMatching(false);
    }
  };

  const handleRankCandidates = async (jobDescription: string) => {
    setIsRanking(true);
    try {
      const candidatesList = [
        {
          candidate_id: "c1",
          candidate_name: "Alice Smith",
          resume_text:
            "Senior Data Scientist with 5 years experience in Python, Scikit-Learn, TensorFlow, SQL, AWS, and Machine Learning algorithms.",
        },
        {
          candidate_id: "c2",
          candidate_name: "Bob Jones",
          resume_text:
            "Full Stack Software Engineer skilled in React, TypeScript, Node.js, HTML, CSS, and AWS Cloud.",
        },
        {
          candidate_id: "c3",
          candidate_name: "Carol White",
          resume_text:
            "Data Analyst with expertise in SQL, Tableau, Power BI, Python, and statistical modeling.",
        },
      ];

      const res = await fetch(`${API_BASE}/rank`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidates: candidatesList, job_description: jobDescription }),
      });
      const data = await res.json();
      if (data.success) {
        setRankings(data.data.rankings);
      }
    } catch (e) {
      alert("Ranking error.");
    } finally {
      setIsRanking(false);
    }
  };

  const handleQuickPredict = async (text: string) => {
    setIsPredicting(true);
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (data.success) {
        setPredictionResult(data.data);
      }
    } catch (e) {
      alert("Prediction connection error.");
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col">
      <Navbar
        isTrained={metricsData?.status === "trained"}
        modelName={metricsData?.model_name}
        onLoadDemo={handleLoadDemo}
        isDemoLoading={isLoadingDemo}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Hackathon Wizard Header */}
        <HackathonWizard
          onLoadDemo={handleLoadDemo}
          onTrain={handleTrainPipeline}
          profileData={profileData}
          metricsData={metricsData}
          isTraining={isTraining}
        />

        {/* Tab Navigation Controls */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab("profiler")}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === "profiler"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <Layers className="h-4 w-4" />
            Dataset & Model Profiler
          </button>

          <button
            onClick={() => setActiveTab("analyzer")}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === "analyzer"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <Brain className="h-4 w-4" />
            Resume Parser & Skill Extractor
          </button>

          <button
            onClick={() => setActiveTab("matcher")}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === "matcher"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <GitCompare className="h-4 w-4" />
            Job Similarity Matcher
          </button>

          <button
            onClick={() => setActiveTab("ranker")}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === "ranker"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <Award className="h-4 w-4" />
            Candidate Ranking Matrix
          </button>
        </div>

        {/* Tab Content Views */}
        {activeTab === "profiler" && (
          <div className="space-y-8">
            <DatasetProfiler
              profileData={profileData}
              onUpload={handleUploadDataset}
              onTrain={handleTrainPipeline}
              isUploading={isUploading}
              isTraining={isTraining}
            />

            <ModelBenchmark metricsData={metricsData} />
          </div>
        )}

        {activeTab === "analyzer" && (
          <div className="space-y-8">
            <ResumeAnalyzer
              onAnalyze={handleAnalyzeResume}
              analysisResult={analysisResult}
              isAnalyzing={isAnalyzing}
            />

            {/* Quick Realtime Prediction Widget */}
            <div className="glass-panel rounded-2xl p-6 border border-slate-800">
              <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                <Cpu className="h-4 w-4 text-indigo-400" />
                Real-Time Role Classification & Feature Explainability
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Test model inference on any sample resume snippet
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. Python Developer with Django FastAPI React SQL experience"
                  className="flex-1 bg-slate-900 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs"
                  id="quickPredictInput"
                />
                <button
                  onClick={() => {
                    const el = document.getElementById("quickPredictInput") as HTMLInputElement;
                    if (el && el.value) handleQuickPredict(el.value);
                  }}
                  disabled={isPredicting}
                  className="gradient-btn px-4 py-2 rounded-xl text-xs font-bold text-white shadow-md disabled:opacity-50"
                >
                  {isPredicting ? "Predicting..." : "Predict Role"}
                </button>
              </div>

              {predictionResult && (
                <div className="mt-4 p-4 bg-slate-900/60 rounded-xl border border-indigo-500/30 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-300">Predicted Job Role:</span>
                    <span className="text-emerald-400 font-bold text-sm">
                      {predictionResult.prediction} ({(predictionResult.confidence * 100).toFixed(1)}%)
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Model Used: <span className="text-slate-200">{predictionResult.model_used}</span>
                  </p>
                  {predictionResult.explanation?.top_terms && (
                    <div className="pt-2 border-t border-slate-800">
                      <span className="text-[11px] text-slate-400 block mb-1">Key Explanatory Words:</span>
                      <div className="flex flex-wrap gap-1">
                        {predictionResult.explanation.top_terms.map((t: any) => (
                          <span
                            key={t.term}
                            className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 text-[10px]"
                          >
                            {t.term} ({t.weight})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "matcher" && (
          <JobMatcher onMatch={handleMatchJob} matchResult={matchResult} isMatching={isMatching} />
        )}

        {activeTab === "ranker" && (
          <CandidateRanker onRank={handleRankCandidates} rankings={rankings} isRanking={isRanking} />
        )}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        ResumeForge AI 2026 — Built for Hackathon Excellence & Dataset Agnostic Intelligence
      </footer>
    </div>
  );
}
