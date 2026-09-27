"use client";
import type { DependenciesInfo } from "../../types/api";

export default function DependenciesCard({ dependencies }: { dependencies: DependenciesInfo }) {
  const runtimeEntries = Object.entries(dependencies.runtime_dependencies)
    .slice(0, 10);

  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Dependencies</h3>
      {dependencies.ecosystems.length > 0 && (
        <div className="mb-2">
          <p className="font-medium">Ecosystems:</p>
          {dependencies.ecosystems.map((e, i) => (
            <span key={i} className="bg-gray-200 px-2 py-1 rounded mr-1">{e}</span>
          ))}
        </div>
      )}
      {dependencies.manifest_files.length > 0 && (
        <div className="mb-2">
          <p className="font-medium">Manifest files:</p>
          {dependencies.manifest_files.map((f, i) => (
            <span key={i} className="bg-gray-200 px-2 py-1 rounded mr-1">{f}</span>
          ))}
        </div>
      )}
      <p>Total dependencies: {dependencies.total_count}</p>
      {runtimeEntries.length > 0 && (
        <div className="mt-2">
          <p className="font-medium">Runtime dependencies:</p>
          <ul className="list-disc list-inside">
            {runtimeEntries.map(([k, v], i) => (
              <li key={i}>{k}= {v}</li>
            ))}
          </ul>
          {Object.entries(dependencies.runtime_dependencies).length > 10 && (
            <p className="text-sm text-gray-600">
              +{Object.entries(dependencies.runtime_dependencies).length - 10} more
            </p>
          )}
        </div>
      )}
    </section>
  );
}
