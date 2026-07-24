# Motion Safety Rules

Plan motion before editing the React + Vite source. Record each effect's target, trigger, purpose, duration, easing, and reduced-motion behavior in `motion-plan.json`.

## Allowed motion

- Use restrained first-view entrance motion to clarify hierarchy.
- Use section reveal only when it improves reading progression.
- Use hover/focus/press feedback for interactive elements.
- Use navigation-state changes and subtle decorative motion when they remain secondary to content.

## Constraints

- Prefer native CSS and lightweight React/DOM logic; do not add a large animation dependency by default.
- Animate `transform` and `opacity` where possible.
- Avoid layout-shifting animation, scroll hijacking, cursor replacement, and continuous distracting loops.
- Keep essential content visible when JavaScript fails.
- Add `@media (prefers-reduced-motion: reduce)` and disable nonessential animation and smooth scrolling.
- Re-run React/Vite source validation, `npm run build`, and three-viewport capture after motion is applied.

On motion rejection, restore the refined source snapshot recorded in `build-state.json` into `.resume-site-work/site/` and revise only the motion plan and motion layer.