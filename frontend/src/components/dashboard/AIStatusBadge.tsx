"use client";
import type { AIResult } from "../../types/api";

export default function AIStatusBadge({ ai }: { ai: AIResult }) {
  const statusColors: Record<string, {bg: string; text: string}> = {
    ok: { bg: "bg-green-100", text: "text-green-800" },
    unavailable: { bg: "bg-yellow-100", text: "text-yellow-800" },
    error: { bg: "bg-red-100", text: "text-red-800" },
  };
  const colors = statusColors[ai.status] || statusColors.unavailable;

  return (
    <div className={"flex items-center space-x-2 " + colors.bg + " " + colors.text + " px-2 py-1 rounded"}>
      <span>{ai.provider}</span>
      {ai.model && <span>{" - "}{ai.model}</span>}
      <span className="font-medium capitalize">{ai.status}</span>
    </div>
  );
}
