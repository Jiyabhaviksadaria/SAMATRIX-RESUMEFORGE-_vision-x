"use client";

import React from "react";
import { Sparkles, Cpu, Zap, Database, CheckCircle2 } from "lucide-react";

interface NavbarProps {
  isTrained: boolean;
  modelName?: string;
  onLoadDemo: () => void;
  isDemoLoading: boolean;
}

export default function Navbar({ isTrained, modelName, onLoadDemo, isDemoLoading }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
            <Zap className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">ResumeForge</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                AI Starter Kit
              </span>
            </div>
            <p className="text-xs text-slate-400">Dataset-Independent Resume Intelligence System</p>
          </div>
        </div>

        {/* System Status & Demo Controls */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <Database className="h-4 w-4 text-indigo-400" />
            <span className="text-slate-300 font-medium">Model:</span>
            {isTrained ? (
              <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {modelName || "Trained Baseline"}
              </span>
            ) : (
              <span className="text-amber-400 font-medium">Untrained</span>
            )}
          </div>

          <button
            onClick={onLoadDemo}
            disabled={isDemoLoading}
            className="gradient-btn px-4 py-2 rounded-xl text-xs font-semibold text-white flex items-center gap-2 shadow-md hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
          >
            <Sparkles className="h-4 w-4 text-amber-300" />
            {isDemoLoading ? "Loading Demo..." : "Load Demo Data"}
          </button>
        </div>
      </div>
    </header>
  );
}
