"""Generate the GitHub profile README from the current public repo list."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen


OWNER = "lsbouchard"
README = "README.md"

REPO_NOTES = {
    "BlochDDFGalerkin": "Python code for Bloch-equation DDF/Galerkin simulations.",
    "SuperExchange": (
        "Research code for symmetry-guided superexchange tensor calculations "
        "in rare-earth-doped silicon spin-qubit systems."
    ),
    "GeoWMSNN": "Research code for geomorphic world-modeling and scientific neural network workflows.",
    "LoopDressedLLB": "Notebook-based research code for loop-dressed Landau-Lifshitz-Bloch modeling.",
    "GradientPathologiesPINNs": (
        "Fork of the Predictive Intelligence Lab repository on gradient pathologies "
        "in physics-informed neural networks."
    ),
}


@dataclass(frozen=True)
class Repo:
    name: str
    url: str
    description: str
    language: str
    is_fork: bool
    updated_at: str


def github_request(url: str) -> list[dict[str, Any]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{OWNER}-profile-readme-generator",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_public_repositories() -> list[Repo]:
    repos: list[Repo] = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/users/{OWNER}/repos"
            f"?type=public&sort=updated&direction=desc&per_page=100&page={page}"
        )
        payload = github_request(url)
        if not payload:
            break
        for item in payload:
            name = item["name"]
            language = item.get("language") or "Mixed / not specified"
            description = item.get("description") or REPO_NOTES.get(name, "Public research/code repository.")
            repos.append(
                Repo(
                    name=name,
                    url=item["html_url"],
                    description=description,
                    language=language,
                    is_fork=bool(item.get("fork")),
                    updated_at=item.get("updated_at", ""),
                )
            )
        page += 1
    return repos


def repo_line(repo: Repo) -> str:
    fork_note = " Fork." if repo.is_fork else ""
    return f"- [{repo.name}]({repo.url}) - {repo.description} `{repo.language}`.{fork_note}"


def render(repos: list[Repo]) -> str:
    profile_repo = [repo for repo in repos if repo.name == OWNER]
    project_repos = [repo for repo in repos if repo.name != OWNER and not repo.is_fork]
    fork_repos = [repo for repo in repos if repo.name != OWNER and repo.is_fork]

    lines = [
        "# Louis-S. Bouchard",
        "",
        "Professor of Chemistry and Biochemistry, UCLA  ",
        "Research software, computational physics, spin dynamics, quantum materials, and scientific computing.",
        "",
        "## Public Repositories",
        "",
        "The GitHub profile overview only shows a small subset of repositories.",
        "",
        "**Browse all public repositories here:**  ",
        f"[github.com/{OWNER}?tab=repositories](https://github.com/{OWNER}?tab=repositories)",
        "",
        "<!-- AUTO-REPOS:START -->",
        f"Currently indexed public repositories: **{len(repos)}**",
        "",
        "### Research And Code",
        "",
    ]
    lines.extend(repo_line(repo) for repo in project_repos)
    if fork_repos:
        lines.extend(["", "### Forks", ""])
        lines.extend(repo_line(repo) for repo in fork_repos)
    if profile_repo:
        lines.extend(["", "### Profile", ""])
        lines.extend(repo_line(repo) for repo in profile_repo)
    lines.extend(
        [
            "<!-- AUTO-REPOS:END -->",
            "",
            "## How This Page Updates",
            "",
            "This profile README is generated from the current public GitHub repository list. "
            "A GitHub Actions workflow refreshes it on a schedule and can also be run manually.",
            "",
            "GitHub profile READMEs are static Markdown files, so they cannot execute code live "
            "each time someone views the page. The scheduled workflow is the closest reliable "
            "GitHub-native equivalent.",
            "",
            "## Notes",
            "",
            "Most repositories here are research artifacts. They are shared for transparency, "
            "reproducibility, and reuse by technically self-sufficient researchers.",
            "",
            "Please check each repository for its own license, citation information, and support policy.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    repos = fetch_public_repositories()
    if not repos:
        raise SystemExit("No public repositories found")
    with open(README, "w", encoding="utf-8") as handle:
        handle.write(render(repos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
