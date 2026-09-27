"use client";
import type { ConfigurationInfo } from "../../types/api";

export default function ConfigurationCard({ configuration }: { configuration: ConfigurationInfo }) {
  const badges = [] as string[];
  if (configuration.has_docker) badges.push("Docker");
  if (configuration.has_docker_compose) badges.push("Docker Compose");
  if (configuration.has_ci) badges.push("CI");
  if (configuration.has_env_example) badges.push("Env Example");
  if (configuration.has_makefile) badges.push("Makefile");

  return (
    <section className="bg-white rounded-lg shadow p-4">
      <h3 className="text-xl font-semibold mb-2">Configuration</h3>
      {badges.length > 0 ? (
        badges.map((b, i) => (
          <span key={i} className="bg-gray-200 px-2 py-1 rounded mr-1">{b}</span>
        ))
      ) : (
        <p>No configuration flags detected</p>
      )}
    </section>
  );
}
