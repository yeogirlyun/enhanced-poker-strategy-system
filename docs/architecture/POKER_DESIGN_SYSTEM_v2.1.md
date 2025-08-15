# 🎨 POKER DESIGN SYSTEM v2.1 — Accessibility-First, Senior-Friendly

> Incremental update focused on **readability**, **menu clarity**, and **enforceable specs** (tokens + code rules). Light & dark themes included. All color pairs meet **WCAG AA** for normal text and **AAA** for large text (≥20px / 1.25rem).

**Status**: Adopt immediately for all new UI; migrate legacy screens per “Adoption Plan” below.  
**Last updated**: 2025‑08‑15

---

## 1) Core Principles
- **Readability over density**: base text never below **16px**; common UI text **18–20px**. Seniors first.
- **High contrast** (minimum AA; AAA for menus, buttons, and key stats). No gray‑on‑gray.
- **Predictable hierarchy**: one scale, one spacing system, one icon grid.
- **Touch‑friendly**: interactive targets ≥ **44×44px** (Apple HIG / WCAG).
- **Focus visible**: keyboard & screen‑reader flows are first‑class.
- **Theme parity**: Light and Dark must be equivalently legible.

---

## 2) Design Tokens (source of truth)
All styling must flow from **semantic tokens** → **component tokens** → raw values. Do **not** hardcode raw hex in components.

### 2.1 Semantic Color Tokens
#### Dark theme (default)
| Token | Value | Usage | Contrast vs background |
|---|---|---|---|
| `--bg` | `#121418` | app background | — |
| `--bg-elev-1` | `#181C22` | panels/cards | — |
| `--bg-elev-2` | `#202632` | menus/dropdowns | — |
| `--content` | `#E6EAF2` | primary text | 12.1:1 on `--bg` |
| `--content-subtle` | `#B8C0CC` | secondary text | 7.9:1 on `--bg` |
| `--muted` | `#8B95A7` | placeholders/disabled | 5.2:1 on `--bg` |
| `--primary` | `#5BA1FF` | primary brand | 4.7:1 on `--bg-elev-2` (buttons AA) |
| `--primary-contrast` | `#0A0C10` | text on primary | 6.8:1 on `--primary` |
| `--success` | `#4CC38A` | positive | AA |
| `--warning` | `#F5C04E` | caution | AA on dark bg |
| `--danger` | `#FF6B6B` | destructive | AA |
| `--accent` | `#A78BFA` | highlights | AA |
| `--border` | `#2B3140` | hairlines | — |
| `--focus` | `#8ACBFF` | focus ring | ≥3:1 vs adjacent |

#### Light theme
| Token | Value | Usage | Contrast vs background |
|---|---|---|---|
| `--bg` | `#FFFFFF` | app background | — |
| `--bg-elev-1` | `#F6F8FB` | panels/cards | — |
| `--bg-elev-2` | `#EEF2F8` | menus/dropdowns | — |
| `--content` | `#111318` | primary text | 16.9:1 on `--bg` |
| `--content-subtle` | `#3C4452` | secondary text | 10.3:1 |
| `--muted` | `#667085` | placeholders/disabled | 6.7:1 |
| `--primary` | `#2563EB` | primary brand | AA on `--bg-elev-2` |
| `--primary-contrast` | `#FFFFFF` | text on primary | 8.1:1 on `--primary` |
| `--success` | `#16A34A` | positive | AA |
| `--warning` | `#B45309` | caution | AA |
| `--danger` | `#DC2626` | destructive | AA |
| `--accent` | `#7C3AED` | highlights | AA |
| `--border` | `#D1D9E6` | hairlines | — |
| `--focus` | `#1D4ED8` | focus ring | ≥3:1 vs adjacent |

> **No raw hex** in code. Always reference semantic tokens.

### 2.2 Typography Tokens
- **Font family**: `Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans", "Apple SD Gothic Neo", "Malgun Gothic", "Helvetica Neue", Arial, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"`
- **Base size**: **18px** (1.125rem)  
- **Scale** (Major Third): 13 → 16 → **18** → 22 → 28 → 36 → 48
  - `--font-xs`: 13px (only for captions/badges; avoid for seniors)
  - `--font-sm`: 16px (supporting text)
  - `--font-base`: **18px** (body, menu items)
  - `--font-lg`: 22px (section headings)
  - `--font-xl`: 28px (tab titles/dialog titles)
  - `--font-2xl`: 36px (page headers)
  - `--font-3xl`: 48px (hero/marketing only)
- **Line height**: 1.5 for body, 1.3 for headings
- **Letter‑spacing**: normal; avoid negative tracking for readability

### 2.3 Spacing & Radius
- **Spacing scale** (px): 4, 8, 12, 16, 20, 24, 32, 40
- **Corner radius**: 8px base; 12px for cards; 16px for modals/menus
- **Elevation**: subtle shadows only; avoid heavy blur
  - Card: `0 1px 2px rgba(0,0,0,.25)`
  - Popover/Menu: `0 6px 16px rgba(0,0,0,.35)`

---

## 3) Menu & Navigation — Senior‑friendly spec
- **Hit area**: ≥ **44×44px** per item (padding Y ≥ 10px, X ≥ 14px).
- **Font**: **18px** menu item text; 16px for secondary description (optional).
- **Colors (dark)**: text `var(--content)`, hover bg `#273044`, active bg `#2F3A50`.
- **Colors (light)**: text `var(--content)`, hover bg `#E9F0FF`, active bg `#DDE8FF`.
- **Focus**: 2px **outside** ring `var(--focus)` + 2px offset shadow for visibility.
- **Icon**: 18–20px; left of label by 8px; maintain consistent visual weights.
- **Section headers**: 16px, uppercase optional, `--content-subtle`.
- **Dividers**: 1px `var(--border)`, full width.
- **Disabled items**: `--muted`, **no** hover/active bg; pointer disabled.

**Dropdowns / Context menus**
- Use `--bg-elev-2` background; border `--border`; radius 12–16px.
- Max height 60vh, enable **type‑ahead** and keyboard navigation.

---

## 4) Component Rules (selected)
### Buttons
- Sizes: **L** (44px), **M** (40px), **S** (36px; avoid for seniors)
- Primary: bg `--primary`, text `--primary-contrast`, hover darken 6–8%
- Secondary: bg `--bg-elev-1`, text `--content`, border `--border`
- Destructive: bg `--danger`, text `--primary-contrast`
- Focus: 2px ring `--focus` + 2px offset
- Minimum width for primary CTAs: 140px

### Inputs
- Font 18px; height ≥ 44px; padding 10/12px
- Text `--content`, placeholder `--muted`
- Border `--border`; focus ring `--focus`
- Error underline or left border using `--danger`

### Tables
- Body text 18px, header 16–18px bold
- Row height ≥ 44px
- Zebra optional using slight alpha on `--content-subtle` (respect contrast)
- On hover: bg `--bg-elev-2` (dark) / `#F3F6FD` (light)

### Cards & Panels
- Radius 12px; padding 16–24px; bg `--bg-elev-1`
- Title 22–28px; subtext 16px `--content-subtle`

### Tabs
- Label 18px; weight 600
- Active indicator 2–3px `--primary`
- Minimum hit area 44×44px

### Badges/Chips
- Text 14–16px; height ≥ 28px
- Color pairs must meet AA on their bg

---

## 5) Accessibility Requirements
- **Contrast**: All text AA; critical nav & buttons **AAA for ≥20px**.
- **Zoom**: UI must function at **200%** zoom (reflow, no clipping).
- **Keyboard**: Every control reachable; visible focus.
- **Screen reader**: aria‑labels for icons; role=menu/menuitem for menus.
- **Motion**: Respect `prefers-reduced-motion`; keep animations ≤200ms.

---

## 6) Implementation — Enforceable Specs

### 6.1 CSS Variables (reference)
```css
:root[color-theme="dark"] {
  --bg:#121418; --bg-elev-1:#181C22; --bg-elev-2:#202632;
  --content:#E6EAF2; --content-subtle:#B8C0CC; --muted:#8B95A7;
  --primary:#5BA1FF; --primary-contrast:#0A0C10;
  --success:#4CC38A; --warning:#F5C04E; --danger:#FF6B6B; --accent:#A78BFA;
  --border:#2B3140; --focus:#8ACBFF;
  --radius-8:8px; --radius-12:12px; --radius-16:16px;
  --font-xs:13px; --font-sm:16px; --font-base:18px; --font-lg:22px; --font-xl:28px; --font-2xl:36px;
}
:root[color-theme="light"] {
  --bg:#FFFFFF; --bg-elev-1:#F6F8FB; --bg-elev-2:#EEF2F8;
  --content:#111318; --content-subtle:#3C4452; --muted:#667085;
  --primary:#2563EB; --primary-contrast:#FFFFFF;
  --success:#16A34A; --warning:#B45309; --danger:#DC2626; --accent:#7C3AED;
  --border:#D1D9E6; --focus:#1D4ED8;
  --radius-8:8px; --radius-12:12px; --radius-16:16px;
  --font-xs:13px; --font-sm:16px; --font-base:18px; --font-lg:22px; --font-xl:28px; --font-2xl:36px;
}
```

### 6.2 Tailwind config example
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        'bg-1': 'var(--bg-elev-1)',
        'bg-2': 'var(--bg-elev-2)',
        content: 'var(--content)',
        'content-subtle': 'var(--content-subtle)',
        muted: 'var(--muted)',
        primary: 'var(--primary)',
        'primary-contrast': 'var(--primary-contrast)',
        success: 'var(--success)',
        warning: 'var(--warning)',
        danger: 'var(--danger)',
        border: 'var(--border)',
        focus: 'var(--focus)',
      },
      borderRadius: {
        DEFAULT: 'var(--radius-8)',
        md: 'var(--radius-12)',
        lg: 'var(--radius-16)',
      },
      fontSize: {
        xs: 'var(--font-xs)',
        sm: 'var(--font-sm)',
        base: 'var(--font-base)',
        lg: 'var(--font-lg)',
        xl: 'var(--font-xl)',
        '2xl': 'var(--font-2xl)',
      },
    }
  }
}
```

### 6.3 React / shadcn defaults
- Use `className="text-base leading-7"` for body; `text-lg` for dense lists; `text-xl font-semibold` for titles.
- Apply `min-h-[44px]` on interactive controls.
- Add `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-2` to all interactive components.

### 6.4 Tkinter theme mapping
- Base font: `('Inter', 12)` → **scaled** by DPI to ~**18px** visual size.
- Menus: font 13–14pt equivalent; item height ≥ 32–36px; padding 8–10px.
- Colors map: window bg → `--bg`, menu bg → `--bg-elev-2`, menu fg → `--content`, focus ring emulate via highlightthickness + `--focus`.

### 6.5 Lint & CI Enforcement
- **Stylelint/ESLint**: disallow raw hex in component CSS/JSX (`--no-hardcoded-colors` custom rule).
- Unit test: snapshot check that `font-size` never below 16px for body text.
- E2E: axe-core run must pass AA contrast; fail CI if violations > 0.
- Precommit: auto‑insert focus ring classes if missing (codemod).

---

## 7) Adoption Plan
1. **Week 1–2**: Introduce tokens + base typography to shell + menus.
2. **Week 3–4**: Migrate tables, tabs, and forms; enforce hit areas.
3. **Week 5**: Dark/light theme completion; add CI checks.
4. **Week 6**: Remove legacy hard‑coded colors; retire v2.0 palette.

---

## 8) Do / Don’t (quick ref)
- ✅ Do use `--font-base` (18px) for menus and body.
- ✅ Do ensure focus ring visible on every control.
- ✅ Do keep contrast AA+.
- ❌ Don’t use text below 16px for anything interactive.
- ❌ Don’t use opacity < 70% for text to “fake” disabled — use `--muted`.
- ❌ Don’t introduce new hex codes without token PR.

---

## 9) Visual Examples (CSS snippets)
```css
.menu {
  background: var(--bg-elev-2);
  color: var(--content);
  border: 1px solid var(--border);
  border-radius: var(--radius-16);
  padding: 8px;
}
.menu__item {
  display: grid;
  grid-template-columns: 20px 1fr auto;
  gap: 8px;
  align-items: center;
  font-size: var(--font-base);
  min-height: 44px;
  padding: 10px 14px;
  border-radius: var(--radius-12);
}
.menu__item:hover { background: #273044; } /* dark */
.menu__item:active { background: #2F3A50; }
.menu__item:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--focus), 0 0 0 4px color-mix(in srgb, var(--bg) 70%, var(--focus) 30%);
}
```

---

**Versioning**
- File: `POKER_DESIGN_SYSTEM_v2.1.md`
- Supersedes: v2.0 menu & typography sections, and all color tokens.
- Owners: Design + Frontend Platforms

