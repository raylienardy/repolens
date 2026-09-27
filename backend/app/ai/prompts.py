import json
from app.analysis.schemas import AnalysisResult

OUTPUT_SCHEMA = {
    "summary": "string, 2-3 paragraf",
    "purpose": "string, 1-2 kalimat",
    "key_technologies": ["string"],
    "architecture_notes": "string",
    "notable_findings": ["string"],
    "improvement_suggestions": ["string"],
    "inference_disclaimer": "string",
}

def build_explanation_prompt(analysis: AnalysisResult) -> str:
    repo = analysis.repository
    lang = analysis.languages
    struct = analysis.structure
    doc = analysis.documentation
    deps = analysis.dependencies
    fwk = analysis.frameworks.detected
    tst = analysis.testing
    cfg = analysis.configuration
    sec = analysis.security_signals
    eps = analysis.entry_points.found

    facts = {
        "repository": {
            "full_name": repo.full_name,
            "description": repo.description,
            "stars": repo.stars,
            "forks": repo.forks,
            "license": repo.license,
            "default_branch": repo.default_branch,
        },
        "languages": {
            "primary": lang.primary,
            "detected": lang.detected,
            "source": lang.source,
        },
        "structure": {
            "total_files": struct.total_files,
            "total_directories": struct.total_directories,
            "top_level_entries": struct.top_level_entries[:30],
            "has_backend_folder": struct.has_backend_folder,
            "has_frontend_folder": struct.has_frontend_folder,
            "has_docs_folder": struct.has_docs_folder,
            "has_tests_folder": struct.has_tests_folder,
        },
        "documentation": {
            "has_readme": doc.has_readme,
            "has_license": doc.has_license,
            "has_contributing": doc.has_contributing,
            "has_changelog": doc.has_changelog,
            "has_docs_folder": doc.has_docs_folder,
            "docs_files_count": doc.docs_files_count,
        },
        "dependencies": {
            "ecosystems": deps.ecosystems,
            "total_count": deps.total_count,
        },
        "frameworks": [
            {"name": f.name, "category": f.category, "confidence": f.confidence}
            for f in fwk
        ],
        "testing": {
            "has_tests_folder": tst.has_tests_folder,
            "test_files_count": tst.test_files_count,
            "has_test_config": tst.has_test_config,
            "has_ci_test_workflow": tst.has_ci_test_workflow,
        },
        "configuration": {
            "has_docker": cfg.has_docker,
            "has_docker_compose": cfg.has_docker_compose,
            "has_ci": cfg.has_ci,
            "has_env_example": cfg.has_env_example,
            "has_makefile": cfg.has_makefile,
        },
        "security_signals": {
            "has_security_md": sec.has_security_md,
            "has_dependabot": sec.has_dependabot,
            "has_env_example": sec.has_env_example,
            "has_gitignore": sec.has_gitignore,
            "has_license": sec.has_license,
            "signals_found": sec.signals_found,
        },
        "entry_points": [{"path": e.path, "kind": e.kind} for e in eps],
    }

    return f"""Kamu asisten yang menjelaskan repository GitHub berdasarkan FAKTA yang diberikan.

# FAKTA REPOSITORY
{json.dumps(facts, indent=2, ensure_ascii=False)}

# TUGAS
Jelaskan repository ini dalam bahasa Indonesia berdasarkan fakta di atas.

# ATURAN
1. JANGAN mengarang informasi yang tidak ada di fakta. Jika tidak ada, tulis "tidak terdeteksi".
2. Jika kamu menyimpulkan sesuatu yang merupakan inferensi, tandai dengan kata "kemungkinan" atau "berdasarkan <fakta>".
3. JANGAN memberi verdict keamanan. Hanya sebutkan file security signal yang ada.
4. JANGAN memberi verdict kualitas absolut (mis. "kode ini bagus/buruk"). JANGAN memberi nilai/skoring.
5. Semua angka harus berasal langsung dari fakta.

# OUTPUT
Kembalikan JSON valid dengan struktur ini, tanpa teks tambahan:
{json.dumps(OUTPUT_SCHEMA, indent=2, ensure_ascii=False)}
"""
