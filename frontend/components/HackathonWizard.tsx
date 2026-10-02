"use client";

import React, { useState } from "react";
import { Sparkles, Layers, Cpu, Play, CheckCircle2, ArrowRight } from "lucide-react";

interface HackathonWizardProps {
  onLoadDemo: () => void;
  onTrain: (targetCol: string, textCols: string[], taskType: string) => void;
  profileData: any;
  metricsData: any;
  isTraining: boolean;
}

export default function HackathonWizard({
  onLoadDemo,
  onTrain,
  profileData,
  metricsData,
  isTraining,
}: HackathonWizardProps) {
  const [activeStep, setActiveStep] = useState(1);

  const steps = [
    { id: 1, title: "1. Profile Dataset", desc: "Upload or load unknown dataset" },
    { id: 2, title: "2. Schema & Task", desc: "Auto-infer target & task type" },
    { id: 3, title: "3. Model Benchmark", desc: "Train & select top baseline" },
    { id: 4, title: "4. Live Prototype", desc: "Demo ready applications" },
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-indigo-500/30 bg-gradient-to-b from-indigo-950/30 to-slate-950/60 mb-8">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-semibold">
              Hackathon Fast-Track Mode
            </span>
            <h2 className="text-lg font-bold text-white">15-Minute Dataset Adaptation Wizard</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Follow these 4 automated steps to adapt ResumeForge to any new hackathon dataset
          </p>
        </div>

        <button
          onClick={onLoadDemo}
          className="gradient-btn px-4 py-2 rounded-xl text-xs font-bold text-white flex items-center gap-2 shadow-lg hover:scale-105 transition-all"
        >
          <Sparkles className="h-4 w-4 text-amber-300" />
          Auto-Run 1-Click Demo
        </button>
      </div>

      {/* Wizard Step Progress */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {steps.map((step) => {
          const isCompleted =
            (step.id === 1 && profileData) ||
            (step.id === 2 && profileData) ||
            (step.id === 3 && metricsData?.status === "trained");
          const isCurrent = activeStep === step.id;

          return (
            <button
              key={step.id}
              onClick={() => setActiveStep(step.id)}
              className={`p-3 rounded-xl border text-left transition-all ${
                isCurrent
                  ? "bg-indigo-600/20 border-indigo-500 text-white shadow-lg shadow-indigo-500/10"
                  : isCompleted
                  ? "bg-slate-900/80 border-emerald-500/30 text-slate-300"
                  : "bg-slate-900/40 border-slate-800 text-slate-500"
              }`}
            >
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span>{step.title}</span>
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : (
                  <ArrowRight className="h-3.5 w-3.5 opacity-50" />
                )}
              </div>
              <p className="text-[11px] opacity-75">{step.desc}</p>
            </button>
          );
        })}
      </div>

      {/* Step Content Preview */}
      <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 text-xs">
        {activeStep === 1 && (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-200 font-medium">Step 1: Dataset Ingestion</p>
              <p className="text-slate-400 mt-0.5">
                {profileData
                  ? `Loaded dataset with ${profileData.rows} rows and ${typeof profileData.columns === "number" ? profileData.columns : profileData.columns_detail?.length || 0} columns.`
                  : "No dataset loaded yet. Load demo dataset or upload a CSV file."}
              </p>
            </div>
            {!profileData && (
              <button
                onClick={onLoadDemo}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg"
              >
                Load Sample Dataset
              </button>
            )}
          </div>
        )}

        {activeStep === 2 && (
          <div>
            <p className="text-slate-200 font-medium">Step 2: Automated Schema & Task Inference</p>
            <p className="text-slate-400 mt-0.5">
              Recommended Task:{" "}
              <span className="text-emerald-400 font-bold uppercase">{profileData?.recommended_task || "Classification"}</span> |
              Suggested Target: <span className="text-indigo-300 font-bold">{profileData?.selected_target || "job_role"}</span>
            </p>
          </div>
        )}

        {activeStep === 3 && (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-200 font-medium">Step 3: Baseline Model Benchmarking</p>
              <p className="text-slate-400 mt-0.5">
                {metricsData?.status === "trained"
                  ? `Selected Best Model: ${metricsData.model_name} with F1 score ${metricsData.metrics?.f1 || "high"}.`
                  : "Click 'Train Pipeline' below to benchmark baselines."}
              </p>
            </div>
            {metricsData?.status !== "trained" && (
              <button
                onClick={() => onTrain(profileData?.selected_target || "job_role", profileData?.text_columns || ["resume_text"], "classification")}
                disabled={isTraining}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg disabled:opacity-50"
              >
                {isTraining ? "Training..." : "Train Pipeline Now"}
              </button>
            )}
          </div>
        )}

        {activeStep === 4 && (
          <div>
            <p className="text-slate-200 font-medium">Step 4: Live Demo Sandbox</p>
            <p className="text-slate-400 mt-0.5">
              Use the tab controls below to test Role Classification, Quality Analysis, Job Match, and Candidate Ranking.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
