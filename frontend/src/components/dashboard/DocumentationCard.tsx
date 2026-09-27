"use client";
import type { DocumentationInfo } from "../../types/api";

export default function DocumentationCard({ documentation }: { documentation: DocumentationInfo }) {
  const items = [
    { label: "Readme", value: documentation.has_readme },
    { label: "License", value: documentation.has_license },
    { label: "Contributing", value: documentation.has_contributing },
    { label: "Changelog", value: documentation.has_changelog },
    { label: "Docs folder", value: documentation.has_docs_folder },
  ];

  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Documentation</h3>
      <ul className="list-disc list-inside">
        {items.map((it) => (
          <li key={it.label}>
            {it.label}: {it.value ? "✓" : "✗"}
          </li>
        ))}
      </ul>
      <p>Docs files count: {documentation.docs_files_count}</p>
    </section>
  );
}
