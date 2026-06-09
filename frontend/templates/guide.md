# Templates guide

This folder contains HTML files that Flask renders into pages visitors and admins can see.

## Folder purposes

- `admin/` contains admin login templates.
- `errors/` contains friendly error pages.
- `flask_admin/` contains customized Flask-Admin templates.
- `layouts/` contains reusable page layouts and navigation.
- `main/` contains public home, about, and contact pages.
- `pages/` contains individual service and information pages.
- `partials/` contains reusable page sections such as headers and footers.
- `track/` contains the shipment tracking page.
- `guide.md` is this plain-language guide to templates.

## BEM conventions for new template work

- Use BEM block names for reusable components, for example `site-nav`, `page-hero`, `feature-card`, `gallery`, and `service-page`.
- Use element classes for component internals, for example `site-nav__link`, `page-hero__title`, and `service-page__section`.
- Use modifier classes for variants, for example `service-page--warehousing` or `service-page__section--overview`.
- Bootstrap classes and local utility classes remain utilities and do not need BEM names.
- During the migration, keep legacy classes next to BEM classes until the compatibility CSS is intentionally removed.
- Run `npm run check:bem` after editing public templates to catch missing BEM hooks.
