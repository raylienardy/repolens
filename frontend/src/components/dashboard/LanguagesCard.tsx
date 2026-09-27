"use client";
import type { LanguagesInfo } from "../../types/api";

export default function LanguagesCard({ languages }: { languages: LanguagesInfo }) {
  const entries = Object.entries(languages.detected)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Languages</h3>
      {languages.primary && (
        <p>Primary: {languages.primary}</p>
      )}
      {entries.length > 0 ? (
        <ul className="list-disc list-inside">
          {entries.map(([ext, count]) => (
            <li key={ext}>{ext}: {count}</li>
          ))}
        </ul>
      ) : (
        <p>No languages detected</p>
      )}
    </section>
  );
}
