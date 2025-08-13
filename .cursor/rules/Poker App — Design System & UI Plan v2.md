Poker App — Design System & UI Plan v2.0

Last updated: 2025-08-12

This plan modernizes the app’s look/feel and interaction model. It prioritizes clarity at the table, quick decision-making, and a premium casino vibe inspired by leading poker titles and best-in-class consumer apps.

⸻

1) Design Principles
	•	Hierarchy first: table actions > info > chrome. Reduce competing colors; use accent sparingly.
	•	Consistency: one spacing scale, one border radius set, predictable states.
	•	Legibility in motion: animations guide attention and never block input.
	•	Accessible by default: 4.5:1 contrast on body text; keyboard and screen-reader friendly.
	•	Low cognitive load: fewer simultaneous choices, clear defaults, progressive disclosure.

⸻

2) Visual Identity — Tokens

Define design tokens to keep the system cohesive across views.

2.1 Core Palette
	•	--bg/base: #0F1318 (Deep graphite)
	•	--bg/surface: #191C22 (Dark charcoal)
	•	--bg/surface-2: #1E232A (Dark slate)
	•	--border/subtle: #2B3440
	•	--border/strong: #2E4F76 (Dark steel blue)
	•	--text/primary: #E8EBEF (Off‑white)
	•	--text/secondary: #8A98A8
	•	--text/muted: #697287
	•	--brand/primary: #3980A6 (Teal blue)
	•	--brand/primary-strong: #2E4F76 (Steel blue)
	•	--brand/secondary: #80A7B5
	•	--accent/gold: #FFD700 (Chips/money)
	•	--success: #4CAF50
	•	--danger: #E53935
	•	--warning: #FFC107
	•	--info: #64B5F6
	•	--focus: #9FDBFF (outline)

2.2 Elevation & Radii
	•	Radius: 6 px (buttons, inputs) · 10 px (cards/panels) · 20 px (modals)
	•	Shadows (RGBA on dark UI):
	•	--shadow/s1: 0 2px 8px rgba(0,0,0,.35)
	•	--shadow/s2: 0 8px 24px rgba(0,0,0,.4)

2.3 Typography
	•	UI: Inter or SF Pro — weights 400/500/600.
	•	Code/monospace: JetBrains Mono (states, logs).
	•	Scale (px): 12, 14, 16, 18, 22, 28.
	•	Default body: 14/20; Buttons: 16/20 semibold; Numbers: tabular-lining.

2.4 Spacing Grid
	•	8‑pt system: 4, 8, 12, 16, 24, 32, 48, 64.
	•	Min tap target: 44×44 px.

⸻

3) Table Presentation

3.1 Felt Themes (ready-to-ship)

Each theme includes a subtle center spotlight (radial gradient 0→60% alpha) and rail contrast.
	1.	Emerald Heritage
Felt #35654D (fine suede + gold thread ring 12px @ 20% opacity).
Rail #4B372B; Table edge ring #2E4F76.
	2.	Midnight Carbon
Felt #242424 (microfiber matte + vignette); Rail #5A4632 bronze; Edge #2E4F76.
	3.	Royal Navy Prestige
Felt #2F4C70 (ripple emboss 5%); Rail #3B2B4C; Edge #2E4F76.

3.2 Seat Frames
	•	Panel: surface‑2 with 10px radius and s1 shadow.
	•	Name: --text/secondary; Stack: --accent/gold; Status chips (Dealer/Turn): pill with brand/primary.
	•	Turn highlight: 2s soft pulse outline (#3980A6 → #80A7B5) + glow.

3.3 Cards
	•	Face: white with 8px radius; thin outline #191C22 @ 60%.
	•	Suits: Red #C0392B; Black #2C3E50.
	•	Hover/selected: shadow s2 + 4px rise.
	•	Back: #2E4F76 with minimal geometric pattern (2% opacity).

⸻

4) Persistent Bottom Panel (Production Spec)

4.1 Container
	•	Background: --bg/surface-2 (#1E232A)
	•	Top border: 2px --border/strong (#2E4F76)
	•	Padding: 8px 16px; Gap: 12px; Layout: grid auto 1fr auto.

4.2 Game Message Area
	•	Container: #2B3845 with subtle top gloss (linear‑grad 0→8% white).
	•	Radius 10px; Padding 10/12; Shadow s1.
	•	Text: --text/primary; secondary lines --text/secondary.
	•	Behavior: cross‑fade 180ms; queue messages; marquee for long notes.

4.3 Buttons

All buttons share: radius 6px; font 600; letter‑spacing .2px; shadow s1; focus ring 2px --focus.
	•	Primary (Bet/All‑in): bg --danger #E53935; hover +8% light; active scale .98; disabled 40% alpha.
	•	Primary‑alt (Check/Call): bg --brand/primary #3980A6; same states.
	•	Secondary (Fold/Cancel): bg #757575; hover #8B8B8B.
	•	Ghost: transparent, 1px border --border/subtle; hover bg rgba(46,79,118,.12).

Sizes
	•	Large (main actions): 44px height, 20px horiz padding, min‑width 120px.
	•	Bet chips (fractions): 36px height, 12px padding, radius 4px; selected state = 2px border #FFD700 + bg lighten 6%.

4.4 Bet Amount Controls
	•	Numeric field: surface bg, 1px border --border/subtle, right‑aligned, stepper buttons (ghost).
	•	Presets grid: 2×4; colors #BF682D (warm orange) except All‑in uses primary (danger).
	•	Keyboard shortcuts shown on hover (e.g., 1/2 → H).

⸻

5) Navigation (Top Menus)
	•	Container: #2E3C54; height 48.
	•	Item default: text --brand/secondary (#80A7B5); hover: lighten to #A0BBCD.
	•	Active: teal pill background #3980A6 + gold underline 2px; text white.
	•	Optional compact tabs: bottom bar 2px --accent/gold only.

⸻

6) Components Library
	•	Chips: denominations with color ring; stack animation (drop/slide 140ms, elastic out).
	•	Toasts (top‑center): success --success, danger --danger, info --brand/primary.
	•	Dialogs/Confirms: modal with scrim rgba(0,0,0,.6); buttons Primary/Secondary per above.
	•	Inputs: 36px height; bg surface; placeholder --text/muted; error border --danger.
	•	Badges: small pill, 12px radius; variants (info/success/danger/warning).

⸻

7) Motion System
	•	Durations: 120–240ms for UI; 300–500ms for table events.
	•	Easing: cubic-bezier(.2,.8,.2,1) (standard), cubic-bezier(.34,1.56,.64,1) (overshoot for chips).
	•	State cues: Your turn pulse; Timer ring countdown; Win pot confetti burst (1s, subtle).

⸻

8) Sound & Haptics
	•	Map events → cues: deal, check, bet, fold, win, error.
	•	Default volume 35%; limit concurrency; duck music during voice lines.

⸻

9) Accessibility & Intl
	•	Contrast: ensure ≥ 4.5:1 for text; ≥ 3:1 for large UI.
	•	Keyboard map: arrows to cycle bet presets; Space to confirm action.
	•	Screen reader: live region for game messages; role=button/slider on controls.
	•	Localize currency/symbols; RTL support for labels.

⸻

10) Theming Packs

Ship 3 presets (swap tokens only):
	•	Emerald Heritage (default)
	•	Midnight Carbon
	•	Royal Navy Prestige

⸻

11) Implementation — Dev Notes

11.1 CSS Variables (excerpt)

:root {
  --bg-base:#0F1318; --bg-surface:#191C22; --bg-surface-2:#1E232A;
  --border-subtle:#2B3440; --border-strong:#2E4F76;
  --text-primary:#E8EBEF; --text-secondary:#8A98A8; --text-muted:#697287;
  --brand-primary:#3980A6; --brand-secondary:#80A7B5; --brand-strong:#2E4F76;
  --accent-gold:#FFD700; --success:#4CAF50; --danger:#E53935; --warning:#FFC107; --info:#64B5F6;
  --focus:#9FDBFF;
}

11.2 Button Class (semantic)

.btn { height:44px; padding:0 20px; border-radius:6px; font-weight:600; box-shadow:0 2px 8px rgba(0,0,0,.35); }
.btn:focus { outline:2px solid var(--focus); outline-offset:2px; }
.btn-primary { background:var(--brand-primary); color:#fff; }
.btn-danger { background:var(--danger); color:#fff; }
.btn-secondary { background:#757575; color:#fff; }
.btn-ghost { background:transparent; border:1px solid var(--border-subtle); }
.btn:hover { filter:brightness(1.08); }
.btn:active { transform:scale(.98); }
.btn[disabled] { opacity:.4; pointer-events:none; }

11.3 Bottom Panel Grid

.bottom-panel { display:grid; grid-template-columns:auto 1fr auto; align-items:center; gap:12px; padding:8px 16px; background:var(--bg-surface-2); border-top:2px solid var(--border-strong); }
.game-msg { background:#2B3845; color:var(--text-primary); border-radius:10px; padding:10px 12px; box-shadow:0 2px 8px rgba(0,0,0,.35); text-align:center; }
.bet-grid { display:grid; grid-template-columns:repeat(4, auto); gap:6px; }
.bet-chip { height:36px; padding:0 14px; border-radius:4px; background:#BF682D; color:#fff; font-weight:600; }
.bet-chip.is-selected { outline:2px solid var(--accent-gold); filter:brightness(1.06); }


⸻

12) QA Checklist
	•	All action buttons meet 44×44px.
	•	Active menu item clearly indicated (pill + underline).
	•	Contrast passes on dark backgrounds.
	•	Keyboard shortcuts function and are discoverable.
	•	Message area truncation handled; live region updates.
	•	Animations under 200ms for UI; no blocking.

⸻

13) Roadmap (Next 2 Sprints)
	1.	Implement tokens + dark theme scaffold.
	2.	Ship bottom panel revamp (spec above).
	3.	Convert menu to pill+underline pattern.
	4.	Card back redesign + asset export pipeline.
	5.	Add analytics for click tracking on bet presets & actions.

⸻

Appendix A — Color Swatches (HEX)

#0F1318, #191C22, #1E232A, #2B3440, #2E3C54, #2E4F76, #3980A6, #80A7B5, #FFD700, #4CAF50, #E53935, #FFC107, #64B5F6

Appendix B — Felt Texture Guidance (Digital)
	•	Fine suede: add monochrome noise 1–2% + soft radial light.
	•	Ripple: 4–6px amplitude, 15–20% opacity overlay.
	•	Gold thread ring: 12px outside felt center, 20% opacity, blur 2px.