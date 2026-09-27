"use client";
import type { AIResult } from "../../types/api";

export default function AIErrorCard({ ai }: { ai: AIResult }) {
  const borderColor = ai.status === "error" ? "border-red-500" : "border-yellow-500";
  return (
    <section className={"border " + borderColor + " rounded-lg p-4 bg-white col-span-2"}>
      <h3 className="text-xl font-semibold mb-2">AI Analysis Unavailable</h3>
      <p className="mb-2">AI analysis tidak tersedia saat ini. Berikut hasil analisis otomatis dari sistem.</p>
      {ai.error_message && (
        <p>Error: <code>{ai.error_message}</code></p>
      )}
      <p>Provider: {ai.provider}</p>
      {ai.model && (
        <p>Model: {ai.model}</p>
      )}
    </section>);
}
