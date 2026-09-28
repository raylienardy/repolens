from datetime import datetime, timezone
from app.ai.schemas import AIExplanation, AIResult
from app.analysis.schemas import AnalysisResult

class MockProvider:
    name = "mock"

    async def generate_explanation(
        self, analysis: AnalysisResult, prompt: str
    ) -> AIResult:
        repo = analysis.repository
        lang = analysis.languages
        struct = analysis.structure
        deps = analysis.dependencies
        tst = analysis.testing
        cfg = analysis.configuration
        sec = analysis.security_signals
        eps = analysis.entry_points.found

        primary_language = lang.primary or "tidak terdeteksi"
        description = repo.description or "tidak memiliki deskripsi"

        summary = (
            f"Repository {repo.full_name} berisi {struct.total_files} file dengan "
            f"bahasa utama {primary_language}. "
            f"Repository ini memiliki {struct.total_directories} direktori, "
            f"{deps.total_count} dependency, dan {len(eps)} entry point terdeteksi. "
            f"Dokumentasi: {'README tersedia' if analysis.documentation.has_readme else 'README tidak terdeteksi'}. "
            f"Testing: {'memiliki folder test' if tst.has_tests_folder else 'tidak memiliki folder test'} "
            f"dengan {tst.test_files_count} file test."
        )

        purpose = (
            f"Berdasarkan metadata repository, repository ini {description}."
        )

        key_technologies = [f.name for f in analysis.frameworks.detected]
        if lang.primary:
            key_technologies.append(lang.primary)
        if not key_technologies:
            key_technologies = ["tidak terdeteksi"]

        architecture_notes = (
            f"Terdeteksi {struct.total_directories} folder utama dan {len(eps)} entry point. "
            f"Top-level entries: {', '.join(struct.top_level_entries[:10]) if struct.top_level_entries else 'tidak terdeteksi'}. "
            f"Ekosistem dependency: {', '.join(deps.ecosystems) if deps.ecosystems else 'tidak terdeteksi'}."
        )

        notable_findings = [
            f"Jumlah file: {struct.total_files}",
            f"Bahasa utama: {primary_language}",
            f"Ekosistem dependency: {', '.join(deps.ecosystems) if deps.ecosystems else 'tidak terdeteksi'}",
            f"Folder test: {'ada' if tst.has_tests_folder else 'tidak ada'} ({tst.test_files_count} file test)",
            f"CI workflow: {'ada' if tst.has_ci_test_workflow else 'tidak ada'}",
            f"Docker: {'ada' if cfg.has_docker else 'tidak ada'}",
            f"README: {'ada' if analysis.documentation.has_readme else 'tidak ada'}",
        ][:7]

        improvement_suggestions = []
        if not sec.has_security_md:
            improvement_suggestions.append("Tambahkan SECURITY.md jika belum ada")
        if not tst.has_tests_folder:
            improvement_suggestions.append("Tambahkan folder tests/ beserta test dasar")
        if not analysis.documentation.has_readme:
            improvement_suggestions.append("Tambahkan README.md untuk mendokumentasikan project")
        if not cfg.has_ci:
            improvement_suggestions.append("Tambahkan CI workflow di .github/workflows/")
        if not improvement_suggestions:
            improvement_suggestions.append("Tidak ada saran spesifik berdasarkan sinyal yang tersedia")

        explanation = AIExplanation(
            summary=summary,
            purpose=purpose,
            key_technologies=key_technologies,
            architecture_notes=architecture_notes,
            notable_findings=notable_findings,
            improvement_suggestions=improvement_suggestions,
            inference_disclaimer=(
                "Ringkasan ini dibuat dari data yang terdeteksi di repository."
            ),
        )

        return AIResult(
            status="ok",
            provider=self.name,
            model="mock-v1",
            explanation=explanation,
            generated_at=datetime.now(timezone.utc),
            prompt_tokens=None,
            completion_tokens=None,
        )
