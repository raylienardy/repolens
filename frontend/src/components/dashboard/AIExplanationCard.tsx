"use client";
import type { AIExplanation } from "../../types/api";
import { stripMarkdown } from "../../lib/text";

export default function AIExplanationCard({ explanation }: { explanation: AIExplanation }) {
  return (
    <section className="bg-white rounded-lg shadow p-4 col-span-2">
      <h3 className="text-xl font-semibold mb-2">AI Explanation</h3>
      <p className="mb-2">{stripMarkdown(explanation.summary)}</p>
      <p className="text-sm text-gray-700 mb-4">{stripMarkdown(explanation.purpose)}</p>
      <div className="flex flex-wrap gap-2 mb-4">
        {explanation.key_technologies.map((tech, i) => (
          <span key={i} className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
            {stripMarkdown(tech)}
          </span>
        ))}
      </div>
      <p className="mb-2">{stripMarkdown(explanation.architecture_notes)}</p>
      <div className="mb-2">
        <p className="font-medium mb-1">Notable Findings:</p>
        <ul className="list-disc list-inside">
          {explanation.notable_findings.map((item, i) => (
            <li key={i}>{stripMarkdown(item)}</li>
          ))}
        </ul>
      </div>
      <div className="mb-2">
        <p className="font-medium mb-1">Improvement Suggestions:</p>
        <ul className="list-disc list-inside">
          {explanation.improvement_suggestions.map((item, i) => (
            <li key={i}>{stripMarkdown(item)}</li>
          ))}
        </ul>
      </div>
      <p className="text-xs text-gray-500 italic mt-4 border-t pt-2">
        {stripMarkdown(explanation.inference_disclaimer)}
      </p>
    </section>
  );
}
