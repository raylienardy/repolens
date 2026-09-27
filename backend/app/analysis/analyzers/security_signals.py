from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import SecuritySignalsInfo

# SIGNALS, bukan verdict. Tidak menyimpulkan keamanan repository.

def analyze_security_signals(input: AnalysisInput) -> SecuritySignalsInfo:
    has_security_md = False
    has_dependabot = False
    has_env_example = False
    has_gitignore = False
    has_license = False

    for entry in input.tree_entries:
        path = entry.get("path", "")
        norm_path = path.lower()
        parts = PurePosixPath(norm_path).parts
        filename = PurePosixPath(norm_path).name

        # has_security_md: root or in .github/
        if filename == "security.md" and (len(parts) == 1 or (len(parts) == 2 and parts[0] == ".github")):
            has_security_md = True

        # has_dependabot: .github/dependabot.yml or .github/dependabot.yaml
        if norm_path in {".github/dependabot.yml", ".github/dependabot.yaml"}:
            has_dependabot = True

        # has_env_example: anywhere in tree
        if filename == ".env.example":
            has_env_example = True

        # has_gitignore: at repository root
        if len(parts) == 1 and filename == ".gitignore":
            has_gitignore = True

        # has_license: LICENSE, LICENSE.md, LICENSE.txt at root
        if len(parts) == 1 and filename in {"license", "license.md", "license.txt"}:
            has_license = True

    # Check repository_metadata for license fallback if present
    if not has_license and input.repository_metadata.get("license"):
        has_license = True

    signals = [has_security_md, has_dependabot, has_env_example, has_gitignore, has_license]
    signals_found = sum(1 for s in signals if s)

    return SecuritySignalsInfo(
        has_security_md=has_security_md,
        has_dependabot=has_dependabot,
        has_env_example=has_env_example,
        has_gitignore=has_gitignore,
        has_license=has_license,
        signals_found=signals_found,
        signals_total=5,
    )
