"use client";

import React from "react";
import { Award, Users } from "lucide-react";

interface CandidateRankerProps {
  onRank: (jobDesc: string) => void;
  rankings: any[];
  isRanking: boolean;
}

export default function CandidateRanker({ onRank, rankings, isRanking }: CandidateRankerProps) {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Award className="h-5 w-5 text-amber-400" />
            Candidate Ranking Matrix
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Rank multiple applicants against job requirements with skill overlap metrics
          </p>
        </div>

        <button
          onClick={() =>
            onRank(
              "Looking for a Senior Data Scientist proficient in Python, SQL, Machine Learning, TensorFlow, and AWS."
            )
          }
          disabled={isRanking}
          className="gradient-btn px-4 py-2 rounded-xl text-xs font-bold text-white flex items-center gap-2 shadow-lg disabled:opacity-50"
        >
          <Users className="h-4 w-4" />
          {isRanking ? "Ranking Applicants..." : "Rank Sample Candidates"}
        </button>
      </div>

      {rankings && rankings.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">Candidate</th>
                <th className="px-4 py-3">Match Score</th>
                <th className="px-4 py-3">Skill Matches</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {rankings.map((c) => (
                <tr key={c.candidate_id} className={c.rank === 1 ? "bg-amber-500/10 font-medium text-white" : ""}>
                  <td className="px-4 py-3 font-bold">#{c.rank}</td>
                  <td className="px-4 py-3">{c.candidate_name}</td>
                  <td className="px-4 py-3 font-bold text-indigo-300">{c.similarity_percentage}</td>
                  <td className="px-4 py-3 text-slate-400">{c.skill_count} skills matched</td>
                  <td className="px-4 py-3">
                    {c.rank === 1 ? (
                      <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px]">
                        Top Applicant
                      </span>
                    ) : (
                      <span className="text-slate-500 text-[10px]">Candidate</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-6 text-xs text-slate-400 bg-slate-900/30 rounded-xl border border-dashed border-slate-800">
          Click &quot;Rank Sample Candidates&quot; to test ranking matrix.
        </div>
      )}
    </div>
  );
}
