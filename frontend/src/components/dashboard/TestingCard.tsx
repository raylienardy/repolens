"use client";
import type { TestingInfo } from "../../types/api";

export default function TestingCard({ testing }: { testing: TestingInfo }) {
  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Testing</h3>
      <ul className="list-disc list-inside">
        <li>Has tests folder: {testing.has_tests_folder ? "✓" : "✗"}</li>
        <li>Test files count: {testing.test_files_count}</li>
        <li>Has test config: {testing.has_test_config ? "✓" : "✗"}</li>
        <li>Has CI test workflow: {testing.has_ci_test_workflow ? "✓" : "✗"}</li>
      </ul>
    </section>
  );
}
