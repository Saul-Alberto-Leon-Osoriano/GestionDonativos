# AGENTS.md

Angular 22 standalone app for "Gestor Solidario de Donativos y Alimentos" (Pastoral San Pio X,
Huancayo). User-facing text and most identifiers are Spanish.

## Commands

- Use npm: `packageManager` is pinned to `npm@11.19.1` and `package-lock.json` is committed.
- `npm start` — dev server at http://localhost:4200.
- `npm run build` — production build. There is no lint or typecheck script; this is the full
  compile + template check.
- `npm run watch` — development build in watch mode.
- `npm test` — Vitest via `@angular/build:unit-test` (not Karma/Jasmine). Use `--watch=false`
  for one-shot runs.
- Single spec: `npx ng test --watch=false --include='**/login.spec.ts'` — the glob is relative
  to `src/`; alternatively filter by suite/test name with `--filter='Login'`.
- Run the built SSR server: `npm run serve:ssr:GestionDonativos`
  (`dist/GestionDonativos/server/server.mjs`).
- Prettier config exists (`.prettierrc`: single quotes, width 100, Angular HTML parser) but there
  is no npm script. Format only files you touch with `npx prettier --write <files>`; the repo
  mixes 2- and 4-space indentation, so do not mass-format.

## Layout and architecture

- `src/app/pages/` — routed pages; `src/app/components/` — reusable page sections.
- Standalone components only; there are no NgModules.
- Every component is a 4-file folder (`name.ts/.html/.css/.spec.ts`). The class drops the suffix
  (`Login`, `Header`, `RegistroDonativos`), and the selector is `app-<kebab-folder>`.
- Pages compose their own `Header`/`Footer`; there is no shared layout shell.
- Routes are declared in `src/app/app.routes.ts` and import page components eagerly.
  `panel-control-principal` and `panel-gestor-usuarios` exist but are not routed yet.
- `app.html` is only `<router-outlet>`; `app.config.ts` provides the router and client hydration.
- Current state is a static front end: no services, HTTP calls, Angular forms bindings, guards,
  or auth logic. The login form is presentational.
- Internal links use plain `href` (full page reload), not `routerLink`. Keep that pattern unless
  deliberately migrating navigation.
- `app.routes.ts` maps both `''` and `inicio` to `LoginPrincipal`; the route segment
  `registrar_encomienda` uses an underscore.
- Keep existing folder names even when they look misspelled, e.g. `targetas-superiores`.
  CSS class naming is inconsistent; do not mass-rename classes.

## Styling

- Bootstrap 5.3.9 and Bootstrap Icons 1.13.2 are loaded from CDN in `src/index.html`. They are
  not npm dependencies and not listed in `angular.json` — do not `npm install bootstrap`.
- Global design tokens (`--azul`, `--dorado`, `--verde`, `--grisclaro`, ...) live in
  `src/styles.css`; component-specific CSS sits beside each component.
- Static assets are served from `public/` at the site root (e.g. `images/Logo-SanPioX.png`).

## SSR and build gotchas

- SSR is enabled: `outputMode: "server"`, `src/server.ts` (Express 5, listens on `PORT` or 4000),
  and every route is prerendered (`RenderMode.Prerender` in `app.routes.server.ts`).
- `npm run build` executes app code in Node. Guard `window`, `document`, `localStorage`, etc., or
  mark a route client-rendered instead of touching browser APIs during construction.
- Production budgets: 500 kB warning / 1 MB error initial; 4 kB / 8 kB per component style.
  Oversized additions fail the build.

## Tests

- Specs are `*.spec.ts` and use Vitest globals (`describe/it/expect`) via `tsconfig.spec.json`.
- Most specs are generated "should create" smoke tests.
- `src/app/app.spec.ts` still asserts the scaffold text `Hello, GestionDonativos`, which
  `app.html` no longer renders. It is expected to fail; don't chase it as a regression.

## Repo notes

- Angular CLI 22.2.6 scaffold. Build outputs `dist/` and `.angular/cache` are gitignored.
- No ESLint, CI, or pre-commit hooks are configured.
