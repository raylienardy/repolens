"use client";
import { useState } from "react";
import AnalyzeForm from "../components/AnalyzeForm";
import type { AnalysisResponse } from "../types/api";
import AnalysisDashboard from "../components/dashboard/AnalysisDashboard";

export default function Home() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-3xl font-bold mb-4">RepoLens</h1>
      <AnalyzeForm onResult={setResult} />
      {result && (
        <AnalysisDashboard
          analysis={result.analysis}
          ai={result.ai}
          fromCache={result.from_cache}
          analyzedAt={result.analyzed_at}
        />
      )}
    </main>
  );
}


