"use client";

import React, { useState } from "react";
import { Search, UserCheck, ShieldCheck, Mail, Phone, Award, Sparkles, Upload } from "lucide-react";

interface ResumeAnalyzerProps {
  onAnalyze: (text: string, candidateName: string) => void;
  analysisResult: any;
  isAnalyzing: boolean;
}

export default function ResumeAnalyzer({ onAnalyze, analysisResult, isAnalyzing }: ResumeAnalyzerProps) {
  const [candidateName, setCandidateName] = useState("Alice Smith");
  const [resumeText, setResumeText] = useState(
    "Alice Smith\nalice.smith@example.com | +1 (555) 234-5678\nSenior Data Scientist with 5 years experience in Python, Scikit-Learn, TensorFlow, SQL, AWS, and Machine Learning algorithms. Bachelor of Science in Computer Science."
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAnalyze(resumeText, candidateName);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <UserCheck className="h-5 w-5 text-indigo-400" />
            Resume Analysis & Skill Extraction
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Extract candidate details, taxonomy skills, and calculate feature completeness quality score
          </p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Form Input */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Candidate Name</label>
            <input
              type="text"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500"
              placeholder="Candidate Name"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Resume Text Content</label>
            <textarea
              rows={8}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl p-3 text-xs focus:ring-2 focus:ring-indigo-500 font-mono leading-relaxed"
              placeholder="Paste resume text or upload document..."
            />
          </div>

          <button
            type="submit"
            disabled={isAnalyzing}
            className="w-full gradient-btn py-2.5 rounded-xl text-xs font-bold text-white flex items-center justify-center gap-2 shadow-lg disabled:opacity-50"
          >
            <Search className="h-4 w-4" />
            {isAnalyzing ? "Analyzing Resume..." : "Run Analysis & Extract Skills"}
          </button>
        </form>

        {/* Results Panel */}
        {analysisResult ? (
          <div className="space-y-4 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
            {/* Contact & Degree */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-white">{analysisResult.candidate?.name}</h3>
                <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                  <span className="flex items-center gap-1">
                    <Mail className="h-3 w-3 text-indigo-400" />
                    {analysisResult.candidate?.email}
                  </span>
                  <span className="flex items-center gap-1">
                    <Phone className="h-3 w-3 text-indigo-400" />
                    {analysisResult.candidate?.phone}
                  </span>
                </div>
              </div>

              {/* Score Gauge */}
              <div className="text-center bg-slate-900 p-2.5 rounded-xl border border-slate-700">
                <span className="text-[10px] uppercase text-slate-400 font-semibold block">Quality Score</span>
                <span className="text-lg font-extrabold text-indigo-400">
                  {analysisResult.quality_analysis?.overall_score}/100
                </span>
              </div>
            </div>

            {/* Detected Skills */}
            <div>
              <h4 className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                <Award className="h-4 w-4 text-amber-400" />
                Detected Skills ({analysisResult.skills?.total_count || 0})
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {analysisResult.skills?.skills?.map((skill: string) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 text-xs font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Section Detection */}
            <div className="pt-2">
              <h4 className="text-xs font-semibold text-slate-400 mb-2">Structure Completeness</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(analysisResult.section_detection || {}).map(([sec, found]) => (
                  <div
                    key={sec}
                    className={`p-2 rounded-lg border flex items-center justify-between ${
                      found
                        ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                        : "bg-slate-900 border-slate-800 text-slate-500"
                    }`}
                  >
                    <span className="capitalize">{sec}</span>
                    <span>{found ? "✓" : "✗"}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 bg-slate-900/30 rounded-xl border border-dashed border-slate-800 text-center">
            <Sparkles className="h-8 w-8 text-slate-600 mb-2" />
            <p className="text-xs text-slate-400">Submit a resume text above to view analysis breakdown</p>
          </div>
        )}
      </div>
    </div>
  );
}
