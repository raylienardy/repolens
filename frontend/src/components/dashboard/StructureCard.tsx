"use client";
import type { StructureInfo } from "../../types/api";

export default function StructureCard({ structure }: { structure: StructureInfo }) {
  const topEntries = structure.top_level_entries.slice(0, 10);

  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Structure</h3>
      <p>Files: {structure.total_files}, Directories: {structure.total_directories}</p>
      <p>Depth Estimate: {structure.depth_estimate}</p>
      {topEntries.length > 0 && (
        <div>
          <p className="mb-1">Top-level entries:</p>
          <ul className="list-disc list-inside">
            {topEntries.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}
      {structure.common_config_files.length > 0 && (
        <div>
          <p className="mb-1">Config files:</p>
          <ul className="list-disc list-inside">
            {structure.common_config_files.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="flex flex-wrap gap-2 mt-2">
        {structure.has_backend_folder && <span className="bg-gray-200 px-2 py-1 rounded">Backend</span>}
        {structure.has_frontend_folder && <span className="bg-gray-200 px-2 py-1 rounded">Frontend</span>}
        {structure.has_docs_folder && <span className="bg-gray-200 px-2 py-1 rounded">Docs</span>}
        {structure.has_tests_folder && <span className="bg-gray-200 px-2 py-1 rounded">Tests</span>}
      </div>
    </section>
  );
}
