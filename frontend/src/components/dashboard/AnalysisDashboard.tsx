"use client";
import type { AnalysisResult, AIResult } from "../../types/api";
import RepositoryHeader from "./RepositoryHeader";
import LanguagesCard from "./LanguagesCard";
import StructureCard from "./StructureCard";
import DocumentationCard from "./DocumentationCard";
import DependenciesCard from "./DependenciesCard";
import FrameworksCard from "./FrameworksCard";
import TestingCard from "./TestingCard";
import ConfigurationCard from "./ConfigurationCard";
import SecuritySignalsCard from "./SecuritySignalsCard";
import EntryPointsCard from "./EntryPointsCard";
import AIExplanationCard from "./AIExplanationCard";
import AIErrorCard from "./AIErrorCard";
import AIStatusBadge from "./AIStatusBadge";
import CacheBadge from "./CacheBadge";

export default function AnalysisDashboard({ analysis, ai, fromCache, analyzedAt }: {
  analysis: AnalysisResult;
  ai: AIResult;
  fromCache: boolean;
  analyzedAt: string;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <CacheBadge fromCache={fromCache} analyzedAt={analyzedAt} />
      <RepositoryHeader repository={analysis.repository} />
      <AIStatusBadge ai={ai} />
      {ai.status === "ok" && ai.explanation ? (
        <AIExplanationCard explanation={ai.explanation} />
      ) : (
        <AIErrorCard ai={ai} />
      )}
      <LanguagesCard languages={analysis.languages} />
      <StructureCard structure={analysis.structure} />
      <DocumentationCard documentation={analysis.documentation} />
      <DependenciesCard dependencies={analysis.dependencies} />
      <FrameworksCard frameworks={analysis.frameworks} />
      <TestingCard testing={analysis.testing} />
      <ConfigurationCard configuration={analysis.configuration} />
      <SecuritySignalsCard security_signals={analysis.security_signals} />
      <EntryPointsCard entry_points={analysis.entry_points} />
    </div>
  );
}
