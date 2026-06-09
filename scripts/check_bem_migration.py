"""Validate the public frontend BEM migration guardrails.

This is intentionally lightweight: it checks that migrated templates keep the
new BEM hooks next to legacy compatibility classes and that service pages carry
page-level blocks/section elements. It is not a full HTML parser, but it gives
CI a fast regression check for the staged BEM rollout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLASS_ATTR_RE = re.compile(r"class=(?P<quote>[\"'])(?P<classes>.*?)(?P=quote)", re.DOTALL)
SECTION_CLASS_RE = re.compile(r"<section\b[^>]*\bclass=(?P<quote>[\"'])(?P<classes>.*?)(?P=quote)", re.DOTALL)
EXTENDS_BASE_RE = re.compile(r"extends\s+[\"']layouts/base\.html[\"']")

REQUIRED_SNIPPETS = {
    "frontend/templates/layouts/base.html": ["l-site", "l-site__main", "site-copyright", "site-copyright__text"],
    "frontend/templates/partials/header.html": ["site-header", "site-header__top-bar"],
    "frontend/templates/partials/menu.html": ["site-nav", "site-nav__toggle", "site-nav__dialog", "site-nav__section", "site-nav__link"],
    "frontend/templates/partials/footer.html": ["site-footer__grid", "site-footer__heading", "site-footer__link", "site-footer__address"],
    "frontend/templates/partials/hero.html": ["hero-carousel", "hero-carousel__slider", "hero-carousel__slide", "hero-carousel__dot"],
    "frontend/templates/partials/about-hero.html": ["page-hero", "page-hero__content", "page-hero__title", "page-hero__subtitle"],
    "frontend/templates/main/index.html": ["feature-card", "feature-card__body", "gallery", "gallery__card", "gallery__dialog-content"],
    "frontend/templates/main/about.html": ["values", "value-card__icon", "value-card__title", "value-card__description"],
    "frontend/templates/track/track.html": ["site-nav", "site-nav__dialog", "site-nav__section", "site-nav__link"],
    "frontend/static/js/menu.js": ["site-nav__dialog--active", "site-nav--scrolled", "site-nav--hidden"],
    "frontend/static/scss/components.scss": [".service-page", ".service-page__section", ".feature-card", ".gallery__image"],
    "frontend/static/assets/scss/components/cards.scss": [".feature-card", ".feature-card__body", ".feature-card__title"],
    "frontend/static/assets/scss/components/gallery.scss": [".gallery__image", ".gallery__dialog", ".gallery__dialog-content"],
    "frontend/static/assets/scss/components/footer/footer.scss": [".site-footer__heading", ".site-footer__link", ".site-copyright"],
    "frontend/static/assets/scss/pages/about/about-us.scss": [".page-hero--about", ".values", ".value-card__icon"],
    "frontend/static/assets/scss/pages/home/index-custom.scss": [".site-nav", ".feature-card", ".gallery__card"],
    "frontend/static/scss/style.scss": [".hero-carousel__content", ".site-nav", ".site-footer__link"],
}

CLASS_PAIR_RULES = {
    "frontend/templates/main/index.html": {
        "card-custom": "feature-card",
        "gallery-link": "gallery__link",
        "gallery-card": "gallery__card",
        "gallery-img": "gallery__image",
        "gallery-overlay": "gallery__overlay",
        "pop-overlay": "gallery__dialog",
        "popup": "gallery__dialog-content",
    },
    "frontend/templates/main/about.html": {
        "values-section": "values",
        "value-icon": "value-card__icon",
        "value-title": "value-card__title",
        "value-description": "value-card__description",
    },
    "frontend/templates/partials/menu.html": {
        "main-menu": "site-nav",
        "mobile-menu-toggle": "site-nav__toggle",
        "menu-modal": "site-nav__dialog",
        "menu-section": "site-nav__section",
        "menu-link": "site-nav__link",
    },
    "frontend/templates/track/track.html": {
        "main-menu": "site-nav",
        "mobile-menu-toggle": "site-nav__toggle",
        "menu-modal": "site-nav__dialog",
        "menu-section": "site-nav__section",
        "menu-link": "site-nav__link",
    },
    "frontend/templates/partials/footer.html": {
        "footer-row": "site-footer__grid",
        "footer-heading": "site-footer__heading",
        "footer-links": "site-footer__list",
        "footer-address": "site-footer__address",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def class_sets(text: str) -> list[set[str]]:
    return [set(match.group("classes").split()) for match in CLASS_ATTR_RE.finditer(text)]


def check_required_snippets(errors: list[str]) -> None:
    for relative, snippets in REQUIRED_SNIPPETS.items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"{relative}: file is missing")
            continue
        text = read(path)
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{relative}: missing required BEM hook `{snippet}`")


def check_class_pairs(errors: list[str]) -> None:
    for relative, pairs in CLASS_PAIR_RULES.items():
        path = ROOT / relative
        text = read(path)
        for classes in class_sets(text):
            for legacy, bem in pairs.items():
                if legacy in classes and bem not in classes:
                    errors.append(f"{relative}: class list with `{legacy}` must also include `{bem}`")


def expected_service_modifier(path: Path) -> str:
    return f"service-page--{path.stem.replace('_', '-')}"


def check_service_pages(errors: list[str]) -> None:
    pages_dir = ROOT / "frontend/templates/pages"
    for path in sorted(pages_dir.glob("*.html")):
        if path.name == "alt.html":
            # Standalone alternate landing page; it does not extend the public layout.
            continue
        text = read(path)
        if not EXTENDS_BASE_RE.search(text):
            continue
        relative = rel(path)
        modifier = expected_service_modifier(path)
        if "service-page" not in text or modifier not in text:
            errors.append(f"{relative}: missing `service-page {modifier}` wrapper")
        sections = list(SECTION_CLASS_RE.finditer(text))
        if not sections:
            errors.append(f"{relative}: expected at least one section with `service-page__section`")
            continue
        for section in sections:
            classes = set(section.group("classes").split())
            if "service-page__section" not in classes:
                errors.append(f"{relative}: section class list `{section.group('classes')}` missing `service-page__section`")


def main() -> int:
    errors: list[str] = []
    check_required_snippets(errors)
    check_class_pairs(errors)
    check_service_pages(errors)

    if errors:
        print("BEM migration check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("BEM migration check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
