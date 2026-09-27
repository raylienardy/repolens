"use client";
import type { AIResult } from "../../types/api";

export default function CacheBadge({ fromCache, analyzedAt }: { fromCache: boolean; analyzedAt: string }) {
  if (fromCache) {
    return (
      <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded col-span-2 text-sm">
        Dari cache – Analisis: {analyzedAt}
      </div>
    );
  }
  return (
    <div className="bg-green-100 text-green-800 px-2 py-1 rounded col-span-2 text-sm">
      Analisis baru
    </div>
  );
}
