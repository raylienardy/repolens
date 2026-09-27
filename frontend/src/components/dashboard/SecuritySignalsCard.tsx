"use client";
import type { SecuritySignalsInfo } from "../../types/api";

export default function SecuritySignalsCard({ security_signals }: { security_signals: SecuritySignalsInfo }) {
  const items = [
    { label: "Security MD", value: security_signals.has_security_md },
    { label: "Dependabot", value: security_signals.has_dependabot },
    { label: "Env example", value: security_signals.has_env_example },
    { label: "Gitignore", value: security_signals.has_gitignore },
    { label: "License", value: security_signals.has_license },
  ];

  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Security Signals</h3>
      <ul className="list-disc list-inside">
        {items.map((it) => (
          <li key={it.label}>
            {it.label}: {it.value ? "✓" : "✗"}
          </li>
        ))}
      </ul>
      <p className="text-sm text-gray-600 mt-2">Ini adalah indikator file-based, bukan penilaian keamanan.</p>
    </section>
  );
}
