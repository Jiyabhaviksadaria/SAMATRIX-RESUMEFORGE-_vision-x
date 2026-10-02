"use client";

import React, { useState } from "react";
import { GitCompare, CheckCircle2, XCircle, ArrowRight } from "lucide-react";

interface JobMatcherProps {
  onMatch: (resumeText: string, jobDesc: string) => void;
  matchResult: any;
  isMatching: boolean;
}

export default function JobMatcher({ onMatch, matchResult, isMatching }: JobMatcherProps) {
  const [resumeText, setResumeText] = useState(
    "Senior Machine Learning Engineer experienced in Python, TensorFlow, PyTorch, SQL, Docker, Scikit-learn, and MLOps deployment on AWS."
  );
  const [jobDescription, setJobDescription] = useState(
    "We are seeking a Lead Data Scientist / ML Engineer with deep expertise in Python, PyTorch, SQL, Kubernetes, AWS, and MLOps."
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onMatch(resumeText, jobDescription);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <GitCompare className="h-5 w-5 text-purple-400" />
            Profile-to-Job Similarity Matcher
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Compare candidate resume against target job description for match score & skill gaps
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Candidate Resume</label>
            <textarea
              rows={4}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl p-3 text-xs focus:ring-2 focus:ring-purple-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target Job Description</label>
            <textarea
              rows={4}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl p-3 text-xs focus:ring-2 focus:ring-purple-500 font-mono"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isMatching}
            className="gradient-btn px-6 py-2.5 rounded-xl text-xs font-bold text-white flex items-center gap-2 shadow-lg disabled:opacity-50"
          >
            <GitCompare className="h-4 w-4" />
            {isMatching ? "Calculating Match..." : "Calculate Job Similarity Score"}
          </button>
        </div>
      </form>

      {matchResult && (
        <div className="mt-6 bg-slate-900/40 p-4 rounded-xl border border-slate-800 space-y-4">
          {/* Match Score Bar */}
          <div>
            <div className="flex justify-between items-center text-xs mb-1">
              <span className="text-slate-300 font-medium">Match Percentage</span>
              <span className="text-indigo-300 font-bold">{matchResult.similarity_percentage}</span>
            </div>
            <div className="w-full bg-slate-900 h-3 rounded-full overflow-hidden border border-slate-700 p-0.5">
              <div
                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
                style={{ width: matchResult.similarity_percentage }}
              />
            </div>
          </div>

          {/* Skill Breakdown */}
          <div className="grid md:grid-cols-2 gap-4 pt-2">
            <div className="bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
              <h4 className="text-xs font-semibold text-emerald-300 mb-2 flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" />
                Matching Required Skills ({matchResult.matching_skills?.length || 0})
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {matchResult.matching_skills?.map((skill: string) => (
                  <span key={skill} className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-200 text-xs">
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
              <h4 className="text-xs font-semibold text-rose-300 mb-2 flex items-center gap-1.5">
                <XCircle className="h-4 w-4" />
                Missing Required Skills ({matchResult.missing_skills?.length || 0})
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {matchResult.missing_skills?.map((skill: string) => (
                  <span key={skill} className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-200 text-xs">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
