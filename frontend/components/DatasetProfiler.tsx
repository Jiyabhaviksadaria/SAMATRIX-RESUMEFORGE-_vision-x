"use client";

import React, { useState } from "react";
import { Upload, FileText, CheckCircle, AlertTriangle, Layers, Play } from "lucide-react";

interface DatasetProfilerProps {
  profileData: any;
  onUpload: (file: File) => void;
  onTrain: (targetCol: string, textCols: string[], taskType: string) => void;
  isUploading: boolean;
  isTraining: boolean;
}

export default function DatasetProfiler({
  profileData,
  onUpload,
  onTrain,
  isUploading,
  isTraining,
}: DatasetProfilerProps) {
  const [selectedTarget, setSelectedTarget] = useState<string>("");
  const [selectedTask, setSelectedTask] = useState<string>("classification");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  const currentTarget = selectedTarget || profileData?.selected_target || profileData?.possible_target_columns?.[0] || "";

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Layers className="h-5 w-5 text-indigo-400" />
            Dataset Profiler & Schema Auto-Detection
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Upload any unknown tabular dataset (.csv, .xlsx) to infer schema and train baselines
          </p>
        </div>

        <label className="cursor-pointer gradient-btn px-4 py-2 rounded-xl text-xs font-semibold text-white flex items-center gap-2">
          <Upload className="h-4 w-4" />
          {isUploading ? "Uploading..." : "Upload New Dataset"}
          <input type="file" accept=".csv,.xlsx" onChange={handleFileChange} className="hidden" />
        </label>
      </div>

      {profileData ? (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Total Rows</span>
              <p className="text-xl font-bold text-white mt-1">{profileData.rows?.toLocaleString() || 0}</p>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Total Columns</span>
              <p className="text-xl font-bold text-white mt-1">
                {typeof profileData.columns === "number" ? profileData.columns : profileData.columns?.length || 0}
              </p>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Detected Text Cols</span>
              <p className="text-xl font-bold text-indigo-300 mt-1">
                {profileData.text_columns?.join(", ") || "None"}
              </p>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Task Recommendation</span>
              <p className="text-sm font-bold text-emerald-400 mt-1 capitalize">
                {profileData.recommended_task} ({(profileData.confidence * 100).toFixed(0)}%)
              </p>
            </div>
          </div>

          {/* Configuration Form */}
          <div className="grid md:grid-cols-2 gap-6 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">Select Target Column</label>
              <select
                value={currentTarget}
                onChange={(e) => setSelectedTarget(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500"
              >
                {(profileData.columns_detail
                  ? profileData.columns_detail.map((c: any) => c.name)
                  : Array.isArray(profileData.columns)
                  ? profileData.columns
                  : []
                ).map((col: string) => (
                  <option key={col} value={col}>
                    {col} {col === profileData.selected_target ? "★ (Auto-Suggested)" : ""}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">Select Task Type</label>
              <select
                value={selectedTask}
                onChange={(e) => setSelectedTask(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500"
              >
                <option value="classification">Classification (Role / Category)</option>
                <option value="matching">Job Similarity Matching</option>
                <option value="ranking">Candidate Ranking</option>
                <option value="skill_extraction">Skill Extraction</option>
                <option value="regression">Regression (Salary / Experience)</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => onTrain(currentTarget, profileData.text_columns || [], selectedTask)}
              disabled={isTraining}
              className="gradient-btn px-6 py-2.5 rounded-xl text-xs font-bold text-white flex items-center gap-2 shadow-lg disabled:opacity-50"
            >
              <Play className="h-4 w-4 fill-white" />
              {isTraining ? "Training Models..." : "Train Pipeline & Benchmark Models"}
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-10 bg-slate-900/30 rounded-xl border border-dashed border-slate-800">
          <FileText className="h-10 w-10 text-slate-500 mx-auto mb-3" />
          <p className="text-sm text-slate-300">No dataset loaded yet.</p>
          <p className="text-xs text-slate-500 mt-1">
            Click &quot;Load Demo Data&quot; at the top or upload a custom CSV dataset to begin.
          </p>
        </div>
      )}
    </div>
  );
}
