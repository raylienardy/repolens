"use client";
import type { EntryPointInfo } from "../../types/api";

export default function EntryPointsCard({ entry_points }: { entry_points: EntryPointInfo }) {
  const { found } = entry_points;
  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Entry Points</h3>
      {found.length > 0 ? (
        <ul className="list-disc list-inside">
          {found.map((ep, i) => (
            <li key={i}>
              {ep.path} – {ep.kind}
              <div className="text-sm text-gray-600">{ep.evidence}</div>
            </li>
          ))}
        </ul>
      ) : (
        <p>No entry points detected</p>
      )}
    </section>
  );
}
