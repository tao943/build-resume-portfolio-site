# React + Vite Output Contract

All stages edit one project at `.resume-site-work/site/`. Do not create a parallel standalone HTML implementation.

## Required project shape

```text
.resume-site-work/site/
├─ package.json
├─ index.html
├─ public/
└─ src/
   ├─ main.jsx (or main.tsx)
   ├─ App.jsx (or App.tsx)
   ├─ components/
   ├─ data/
   └─ styles/
```

Equivalent component boundaries are allowed. The project must use React, React DOM, and Vite, and `package.json` must expose working `dev` and `build` scripts.

## Content and layout contract

The first runnable prototype must contain:

- a near-full-screen Hero with navigation, a primary heading, contact action, and safe video/media fallback;
- a personal experience or about region with only supplied facts;
- a featured projects region;
- an evidence-based strengths region;
- a contact closing region.

Use centralized resume/portfolio data and CSS custom properties for design tokens. Target an approximately 1700px desktop content width while preventing horizontal overflow on tablet and 390px mobile widths.

Do not fabricate resume facts, metrics, links, photos, screenshots, or remote videos. Omit absent contact channels. Use neutral, explicit fallbacks for missing media.

## Safety and accessibility

- Reject `javascript:` and `data:text/html` URLs.
- Preserve semantic headings, keyboard navigation, visible focus, readable contrast, and alt text.
- The motion stage must include `prefers-reduced-motion: reduce` behavior.
- Avoid dependency changes unless they are necessary and approved.

## Validation and preview

Validate source before building:

```powershell
python <skill-root>/scripts/validate_vite_project.py .resume-site-work/site --stage prototype
```

Use `styled`, `refined`, or `motion` for later stages. Then run from `.resume-site-work/site/`:

```powershell
npm run build
```

Only a successful `dist/` build may be copied to `.resume-site-work/preview/dist/`, captured, or shown at a confirmation gate. Source validation does not replace a real Vite build.