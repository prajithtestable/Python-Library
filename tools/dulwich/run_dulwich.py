#!/usr/bin/env python3
# TODO(data-platform): unify CLI output formatting across tool runners.
"""Repository mining with dulwich -- Python 3.12 branch.

dulwich 1.2.12 is pinned on this branch. This is the sharpest dependency split
in the matrix: py3.9 gets dulwich 0.24.x and every other branch gets 1.2.x, a
major-version boundary. Any API drift between them shows up here.

dulwich is a pure-Python git implementation, so this runs with no git binary
on PATH. It replaces pydriller from the C# repository's tool set.

Reports: commit count, author ownership, per-file churn and change coupling.
"""

from collections import Counter, defaultdict
from pathlib import Path

from dulwich.repo import Repo

REPO_ROOT = Path(__file__).resolve().parents[2]


def decode(value):
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)


def changed_paths(repo, commit):
    """Paths touched by a commit, relative to its first parent."""
    if not commit.parents:
        tree_before = None
    else:
        tree_before = repo[commit.parents[0]].tree
    changes = repo.object_store.tree_changes(tree_before, commit.tree)
    touched = set()
    for (old_path, new_path), _modes, _shas in changes:
        for path in (old_path, new_path):
            if path:
                touched.add(decode(path))
    return touched


def main() -> int:
    import dulwich

    print(f"[dulwich] version {dulwich.__version__}")

    repo = Repo(str(REPO_ROOT))
    try:
        walker = list(repo.get_walker())
    except KeyError:
        print("[dulwich] no commits found")
        return 0

    authors = Counter()
    contributors = Counter()
    per_file_commits = Counter()
    per_file_authors = defaultdict(set)
    cochange = Counter()
    messages = []

    for entry in walker:
        commit = entry.commit
        author = decode(commit.author)
        authors[author] += 1
        contributors[author] += 1
        message = decode(commit.message)
        # Co-authored-by trailers are part of authorship for ownership
        # metrics; counting only the commit author understates the team.
        for line in message.splitlines():
            if line.lower().startswith("co-authored-by:"):
                contributors[line.split(":", 1)[1].strip()] += 1
        messages.append((decode(commit.id)[:8], author, message.strip().splitlines()[0]))

        touched = {p for p in changed_paths(repo, commit) if p.endswith(".py")}
        for path in touched:
            per_file_commits[path] += 1
            per_file_authors[path].add(author)
        # Commits touching a very large number of files (bulk wiring) drown
        # out real coupling, so they are excluded from the coupling matrix.
        ordered = sorted(touched) if len(touched) <= 8 else []
        for i, left in enumerate(ordered):
            for right in ordered[i + 1 :]:
                cochange[(left, right)] += 1

    print(f"[dulwich] commits on HEAD : {len(messages)}")
    print()

    print("  Commit authorship")
    for author, count in authors.most_common():
        share = 100.0 * count / len(messages)
        print(f"    {count:>3}  ({share:5.1f}%)  {author}")

    print()
    print("  Contributor ownership (author + Co-authored-by trailers)")
    for person, count in contributors.most_common():
        share = 100.0 * count / len(messages)
        print(f"    {count:>3}  ({share:5.1f}%)  {person}")

    print()
    print("  Churn -- most frequently modified Python files")
    for path, count in per_file_commits.most_common(10):
        owners = len(per_file_authors[path])
        print(f"    {count:>3} commits  {owners} author(s)  {path}")

    print()
    print("  Change coupling -- files that keep changing together")
    coupled = [pair for pair in cochange.most_common(10) if pair[1] > 1]
    if not coupled:
        print("    (none above threshold)")
    for (left, right), count in coupled:
        print(f"    {count:>3}x  {left}  +  {right}")

    print()
    print("  Recent history")
    for sha, author, subject in messages[:10]:
        name = author.split("<")[0].strip()
        print(f"    {sha}  {name:<22} {subject}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
