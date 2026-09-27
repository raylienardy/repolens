"use client";
import React, { useState } from "react";
import { analyzeRepo } from "../lib/api";
import type { AnalysisResponse } from "../types/api";

interface AnalyzeFormProps {
  onResult: (data: AnalysisResponse) => void;
}

export default function AnalyzeForm({ onResult }: AnalyzeFormProps) {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = repoUrl.trim();
    if (!trimmed) {
      setError("Please provide a repository URL");
      return;
    }
    if (!trimmed.includes("github.com")) {
      setError("URL must contain github.com");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await analyzeRepo(trimmed);
      onResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze repository");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-lg flex flex-col gap-2">
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="https://github.com/owner/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          disabled={loading}
          className="flex-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </form>
  );
}
