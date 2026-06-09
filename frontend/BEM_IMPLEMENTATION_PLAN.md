# Frontend BEM implementation plan

This plan moves the public frontend toward predictable BEM class names without forcing a risky one-shot rewrite. Each stage keeps legacy classes until the owning templates and CSS have been migrated and verified.

## BEM conventions

- **Blocks** use concise component names: `site-header`, `site-footer`, `service-card`, `page-hero`.
- **Elements** use double underscores and only describe children of a block: `site-footer__heading`, `site-footer__link`.
- **Modifiers** use double hyphens for variants: `service-card--featured`, `page-hero--compact`.
- **Utilities remain utilities**. Bootstrap classes and local utilities such as `text-primary-color`, `bg-section-1`, spacing, grid, and flex helpers stay outside BEM.
- **Migration is additive first**. During migration, templates may carry both legacy and BEM classes so existing CSS and tests remain stable.

## Stage 1 — Foundation and shared shell

- Document the BEM naming rules and the five-stage rollout.
- Add BEM classes to the common public shell, header, footer, and copyright templates while preserving existing classes.
- Add CSS selectors for the new shell/footer BEM names beside existing legacy selectors.
- Verify SCSS compilation and existing frontend/admin tests affected by shared templates.

## Stage 2 — Navigation and hero components

- Migrate `partials/menu.html`, `partials/hero.html`, and `partials/about-hero.html` to BEM blocks.
- Consolidate menu and hero selectors currently spread across global styles and page styles.
- Keep Bootstrap layout classes as utilities; remove only redundant legacy component classes after screenshots/tests pass.

## Stage 3 — Reusable cards, service sections, and galleries

- Standardize cards with `service-card`, `value-card`, `feature-card`, and `gallery` blocks.
- Move shared card styling from page-specific CSS into component CSS/SCSS.
- Update service pages that already share section patterns before changing unique pages.

## Stage 4 — Page-level service templates

- Convert each `frontend/templates/pages/` service page to page blocks such as `service-page`, `service-page__section`, and targeted modifiers.
- Remove duplicated selectors from page SCSS once shared BEM components cover them.
- Run visual checks for representative service pages.

## Stage 5 — Cleanup and enforcement

- Remove legacy class aliases no longer used by templates.
- Add lint/documentation checks that discourage new non-BEM component selectors.
- Update frontend guides with examples for future pages and components.
