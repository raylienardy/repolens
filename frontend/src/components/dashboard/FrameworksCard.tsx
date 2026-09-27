"use client";
import type { FrameworksInfo, DetectedFramework } from "../../types/api";

function confidenceBadge(conf: string) {
  const colors: Record<string, string> = {
    high: "bg-green-200 text-green-800",
    medium: "bg-yellow-200 text-yellow-800",
    low: "bg-gray-200 text-gray-800",
  };
  return colors[conf.toLowerCase()] || "bg-gray-200 text-gray-800";
}

export default function FrameworksCard({ frameworks }: { frameworks: FrameworksInfo }) {
  const { detected } = frameworks;

  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Frameworks</h3>
      {detected.length > 0 ? (
        <ul className="list-disc list-inside">
          {detected.map((fw, i) => (
            <li key={i} className="mb-2">
              <span className="font-medium">{fw.name}</span> – {fw.category}{" "}
              <span className={confidenceBadge(fw.confidence)}>{fw.confidence}</span>
              <div className="text-sm text-gray-600">{fw.evidence}</div>
            </li>
          ))}
        </ul>
      ) : (
        <p>No frameworks detected</p>
      )}
    </section>
  );
}
