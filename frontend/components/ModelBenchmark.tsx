"use client";

import React from "react";
import { Trophy, BarChart3, Clock, CheckCircle } from "lucide-react";

interface ModelBenchmarkProps {
  metricsData: any;
}

export default function ModelBenchmark({ metricsData }: ModelBenchmarkProps) {
  if (!metricsData || metricsData.status !== "trained") {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 text-center py-8">
        <Trophy className="h-8 w-8 text-slate-600 mx-auto mb-2" />
        <p className="text-sm text-slate-400">Model Leaderboard available after dataset training.</p>
      </div>
    );
  }

  const { model_name, metrics, leaderboard, feature_importance } = metricsData;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-400" />
            Model Evaluation Leaderboard
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated model benchmarking comparing lightweight baselines
          </p>
        </div>

        <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg text-xs font-semibold flex items-center gap-1.5">
          <CheckCircle className="h-3.5 w-3.5" />
          Best Model: {model_name}
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
            <tr>
              <th className="px-4 py-3">Rank</th>
              <th className="px-4 py-3">Model</th>
              <th className="px-4 py-3">Primary Score</th>
              <th className="px-4 py-3">Accuracy</th>
              <th className="px-4 py-3">Train Time</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {leaderboard?.map((item: any, idx: number) => (
              <tr key={item.name} className={idx === 0 ? "bg-indigo-500/10 font-medium text-white" : ""}>
                <td className="px-4 py-3">#{idx + 1}</td>
                <td className="px-4 py-3">{item.name}</td>
                <td className="px-4 py-3 font-bold text-indigo-300">{item.primary_score?.toFixed(4)}</td>
                <td className="px-4 py-3">{item.metrics?.accuracy ? (item.metrics.accuracy * 100).toFixed(1) + "%" : "N/A"}</td>
                <td className="px-4 py-3 flex items-center gap-1 text-slate-400">
                  <Clock className="h-3 w-3" />
                  {item.train_time_sec?.toFixed(2)}s
                </td>
                <td className="px-4 py-3">
                  {idx === 0 ? (
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px]">
                      Selected
                    </span>
                  ) : (
                    <span className="text-slate-500 text-[10px]">Evaluated</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Global Feature Importance */}
      {feature_importance && feature_importance.length > 0 && (
        <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800">
          <h3 className="text-xs font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-indigo-400" />
            Top Feature Importances (TF-IDF Attribution)
          </h3>
          <div className="flex flex-wrap gap-2">
            {feature_importance.slice(0, 10).map((feat: any) => (
              <span
                key={feat.feature}
                className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-xs text-indigo-200 flex items-center gap-1.5"
              >
                <span>{feat.feature}</span>
                <span className="text-[10px] text-slate-400 font-mono">({feat.importance?.toFixed(3)})</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
