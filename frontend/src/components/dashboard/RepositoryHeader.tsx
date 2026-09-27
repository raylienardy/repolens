"use client";
import type { RepositoryInfo } from "../../types/api";

export default function RepositoryHeader({ repository }: { repository: RepositoryInfo }) {
  return (
    <section className="bg-white rounded-lg shadow p-4 col-span-2">
      <h2 className="text-2xl font-bold mb-2">{repository.full_name}</h2>
      {repository.description && <p className="mb-2">{repository.description}</p>}
      <div className="flex flex-wrap gap-2 text-sm">
        <span>⭐ {repository.stars}</span>
        <span>🍴 {repository.forks}</span>
        {repository.license && <span>License: {repository.license}</span>}
        <a
          href={repository.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          View on GitHub
        </a>
      </div>
    </section>
  );
}
