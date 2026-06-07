"""Verify every tracked CSS stylesheet has a matching SCSS source file.

This check intentionally does not compile or rewrite CSS. Pair it with
`npm run check:scss` to validate Sass parsing without touching committed CSS.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", "node_modules", ".scss-build"}


def scss_counterpart(css_path: Path) -> Path | None:
    """Return the expected SCSS source path for a static CSS file."""
    parts = css_path.parts

    if parts[:4] == ("frontend", "static", "assets", "css"):
        return Path(*parts[:3], "scss", *parts[4:]).with_suffix(".scss")

    if parts[:3] == ("frontend", "static", "css"):
        return Path("frontend", "static", "scss", *parts[3:]).with_suffix(".scss")

    if parts[:3] == ("admin", "static", "css"):
        return Path("admin", "static", "scss", *parts[3:]).with_suffix(".scss")

    return None


def tracked_css_files() -> list[Path]:
    """Find CSS files in the repository, excluding generated/dependency trees."""
    css_files: list[Path] = []
    for path in ROOT.rglob("*.css"):
        relative_path = path.relative_to(ROOT)
        if IGNORED_PARTS.intersection(relative_path.parts):
            continue
        css_files.append(relative_path)
    return sorted(css_files)


def main() -> int:
    missing_pairs: list[tuple[Path, Path]] = []
    unmapped_css: list[Path] = []

    for css_path in tracked_css_files():
        expected_scss = scss_counterpart(css_path)
        if expected_scss is None:
            unmapped_css.append(css_path)
            continue
        if not (ROOT / expected_scss).exists():
            missing_pairs.append((css_path, expected_scss))

    if unmapped_css or missing_pairs:
        print("SCSS migration verification failed.")
        if unmapped_css:
            print("\nCSS files without a known SCSS mapping:")
            for css_path in unmapped_css:
                print(f"- {css_path}")
        if missing_pairs:
            print("\nCSS files missing SCSS counterparts:")
            for css_path, expected_scss in missing_pairs:
                print(f"- {css_path} -> {expected_scss}")
        return 1

    css_count = len(tracked_css_files())
    print(f"SCSS migration verification passed: {css_count} CSS files have SCSS counterparts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
